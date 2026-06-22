"""
This module contains tests for the FirestoreHandler class to ensure interactions with Firestore instances
are working as expected.
"""

import pytest
import requests
from google.api_core.exceptions import RetryError

from eq_cims_management_ui.utils.database.firestore_handler import FirestoreHandler


@pytest.mark.usefixtures("mock_valid_cir_requests", "mock_firestore_session")
def test_create_database_session():
    """
    Test that a new session document is created in a mock Firestore instance with the expected
    data when the create_database_session method is called.
    """
    firestore_handler = FirestoreHandler()

    firestore_handler.create_database_session()

    assert firestore_handler.latest_session_document_ref is not None
    assert firestore_handler.latest_session_document_ref.get().to_dict() == {
        "created_at": "2026-05-05T15:00:43.198172+01:00",
        "status": "Not started",
    }


@pytest.mark.usefixtures("mock_valid_cir_requests", "mock_erroneous_firestore_session")
def test_create_session_fails():
    """
    Test that an exception is raised when the create_database_session method fails to create a new
    session given an erroneous Firestore instance.
    """
    firestore_handler = FirestoreHandler()

    with pytest.raises(RetryError):
        firestore_handler.create_database_session()
        assert firestore_handler.latest_session_document_ref is None


@pytest.mark.usefixtures("mock_erroneous_cir_status")
def test_create_session_fails_with_cir_connection_error():
    """
    Test that when trying to create a new session, a 'requests.exception.ConnectionError' exception is raised when CIR
    is not available.
    """
    firestore_handler = FirestoreHandler()

    with pytest.raises(requests.exceptions.ConnectionError):
        firestore_handler.create_database_session()
        assert firestore_handler.latest_session_document_ref is None


@pytest.mark.usefixtures("mock_invalid_cir_metadata_requests")
def test_empty_cir_metadata_response():
    """
    Test that when trying to create a new session, a 'ValueError' exception is raised when CIR returns an empty
    response for collection instrument metadata.
    """
    firestore_handler = FirestoreHandler()

    with pytest.raises(ValueError):
        firestore_handler.create_database_session()
        assert firestore_handler.latest_session_document_ref is None


@pytest.mark.usefixtures("mock_retrieve_latest_session")
def test_retrieve_latest_session():
    """
    Test that the retrieve_latest_session method returns the expected session ID when a latest session document is
    present and the status is not 'Not started'.
    """
    firestore_handler = FirestoreHandler()

    latest_session = firestore_handler.retrieve_latest_session()

    assert latest_session is not None
    assert latest_session == "abc-def-ghi"


@pytest.mark.usefixtures("mock_retrieve_latest_session_not_present")
def test_retrieve_latest_session_no_session():
    """Test that the retrieve_latest_session method returns None when no latest session document is present."""
    firestore_handler = FirestoreHandler()

    latest_session = firestore_handler.retrieve_latest_session()

    assert latest_session is None


@pytest.mark.usefixtures("mock_retrieve_latest_session_failure")
def test_retrieve_latest_session_failure():
    """
    Test that the retrieve_latest_session method returns None when a RetryError occurs while retrieving the
    latest session.
    """
    with pytest.raises(RetryError):
        firestore_handler = FirestoreHandler()
        latest_session = firestore_handler.retrieve_latest_session()
        assert latest_session is None


@pytest.mark.usefixtures("mock_document_reference")
def test_set_document_reference(mock_document_reference):
    """Test that the set_document_reference method sets the latest_session_document_ref attribute correctly."""
    firestore_handler = FirestoreHandler()

    firestore_handler.set_document_reference(mock_document_reference)

    assert firestore_handler.latest_session_document_ref is not None
    assert firestore_handler.latest_session_document_ref.id == "abc-def-ghi"


@pytest.mark.usefixtures("mock_valid_cir_requests", "mock_update_session_status")
def test_update_session_status(mock_update_session_status):
    """Test that the update_firestore_session_status method updates the status of the latest session document."""
    firestore_handler = FirestoreHandler()
    firestore_handler.latest_session_document_ref = mock_update_session_status

    assert firestore_handler.latest_session_document_ref.get().to_dict()["status"] == "Not started"

    firestore_handler.update_firestore_session_status("Running")

    assert firestore_handler.latest_session_document_ref.get().to_dict()["status"] == "Running"


@pytest.mark.usefixtures("mock_valid_cir_requests", "mock_update_ci_status")
def test_update_ci_status(mock_update_ci_status):
    """Test that the update_ci_status method updates the status of a collection instrument document."""
    firestore_handler = FirestoreHandler()
    firestore_handler.latest_session_document_ref, subcollection = mock_update_ci_status

    assert subcollection.document("abc-def-ghi").get().to_dict()["status"] == "Not started"

    firestore_handler.update_firestore_ci_status("xyz", "Success")

    assert subcollection.document("abc-def-ghi").get().to_dict()["status"] == "Success"

    # latest_session_document_ref.collection("metadata").document(ci_guid).get().to_dict()["status"],
