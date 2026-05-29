"""This module contains tests for the firestore_logic module to ensure business logic is working as expected."""

import pytest
from google.api_core.exceptions import RetryError

from eq_cims_management_ui.utils.database.firestore_logic import (
    create_new_session,
    get_collection_instruments,
    is_latest_session_present,
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
        "ci_version": 1,
        "data_version": "0.0.1",
        "validator_version": "0.0.1",
        "classifier_type": "form_type",
        "classifier_value": "1234",
        "guid": "xyz",
        "language": "en",
        "published_at": "2026-05-21T13:57:24.276672Z",
        "survey_id": "999",
        "title": "Test Survey",
        "status": "Not started",
    }

    assert test_ci_metadata[1] == {
        "ci_version": 1,
        "data_version": "0.0.1",
        "validator_version": "0.0.1",
        "classifier_type": "form_type",
        "classifier_value": "1234",
        "guid": "abc",
        "language": "en",
        "published_at": "2026-05-21T13:56:55.905000Z",
        "survey_id": "999",
        "title": "Test Survey 2",
        "status": "Not started",
    }


@pytest.mark.usefixtures("mock_invalid_firestore_metadata_stream")
def test_get_collection_instruments_fails():
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
    for fixture in fixtures:
        request.getfixturevalue(fixture)

    is_latest_session = is_latest_session_present()
    assert is_latest_session == expected_result
