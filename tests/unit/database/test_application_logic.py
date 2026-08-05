"""This module contains tests for the firestore_logic module to ensure business logic is working as expected."""

import pytest
from google.api_core.exceptions import RetryError

from eq_cims_management_ui.utils.database.application_logic import (
    create_new_session,
    get_collection_instruments,
    is_latest_session_in_progress,
    update_ci_status,
    update_session_status,
)


@pytest.mark.usefixtures("mock_create_database_session")
def test_create_session(mock_create_database_session):
    """Test that the create_new_session function calls the correct methods from the FirestoreHandler class."""
    create_new_session()

    assert mock_create_database_session.call_count == 1


@pytest.mark.usefixtures("mock_firestore_ci_metadata_stream")
def test_get_collection_instruments():
    """Test that the get_collection_instruments function returns the expected collection instrument metadata."""
    test_ci_metadata = get_collection_instruments()

    assert test_ci_metadata is not None
    assert len(test_ci_metadata) == 2
    assert test_ci_metadata[0] == {
        "survey_id": "999",
        "form_type": "1234",
        "cir_id": "275229fc-9b2e-438d-8a21-4a69b272575a",
        "cir_version": 1,
        "publish_date": "2026-05-21T13:59:24.276672Z",
        "validator_version": "0.0.1",
        "status": "Not started",
        "error_message": "None",
    }

    assert test_ci_metadata[1] == {
        "survey_id": "999",
        "form_type": "1234",
        "cir_id": "64faab81-b4e1-4c3d-9c54-1632ad34af4e",
        "cir_version": 2,
        "publish_date": "2026-05-21T13:59:24.276672Z",
        "validator_version": "0.0.1",
        "status": "Not started",
        "error_message": "None",
    }


@pytest.mark.usefixtures("mock_invalid_firestore_metadata_stream")
def test_get_collection_instruments_fails():
    """Test that get_collection_instruments returns None when the Firestore stream fails."""
    with pytest.raises(RetryError):
        test_erroneous_ci_metadata = get_collection_instruments()
        assert test_erroneous_ci_metadata is None


@pytest.mark.parametrize(
    "fixtures, expected_result",
    [
        (("mock_retrieve_latest_session", "mock_firestore_get_session"), False),
        (("mock_retrieve_latest_session", "mock_firestore_get_session_no_session"), False),
        (("mock_retrieve_latest_session", "mock_firestore_get_session_in_progress"), True),
    ],
)
def test_is_latest_session_present(request, fixtures, expected_result):
    """
    Test that the is_latest_session_present function returns the expected result depending on if the latest session
    is present, not present or in progress.
    """
    for fixture in fixtures:
        request.getfixturevalue(fixture)

    is_latest_session = is_latest_session_in_progress()
    assert is_latest_session == expected_result


@pytest.mark.usefixtures("mock_firestore_update_session_status")
def test_update_session_status(mock_firestore_update_session_status):
    """Test that the update_firestore_session_status function updates the session status correctly."""
    update_session_status("Running")

    assert mock_firestore_update_session_status.call_count == 1


@pytest.mark.usefixtures("mock_firestore_update_ci_status")
def test_update_ci_status(mock_firestore_update_ci_status):
    """Test that the update_ci_status function updates the collection instrument status correctly."""
    update_ci_status("64faab81-b4e1-4c3d-9c54-1632ad34af4e", "Success")

    assert mock_firestore_update_ci_status.call_count == 1
