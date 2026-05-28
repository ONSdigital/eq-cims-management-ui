"""
This module contains tests for the FirestoreHandler class to ensure interactions with Firestore instances
are working as expected.
"""
import logging

import pytest
import requests
from google.api_core.exceptions import RetryError
from structlog.testing import capture_logs

from eq_cims_management_ui.utils.database.firestore_handler import FirestoreHandler
from tests.unit.conftest import mock_invalid_cir_metadata_requests, mock_valid_cir_requests


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
    firestore_handler = FirestoreHandler()

    with pytest.raises(requests.exceptions.ConnectionError):
        firestore_handler.create_database_session()
        assert firestore_handler.latest_session_document_ref is None


@pytest.mark.usefixtures("mock_invalid_cir_metadata_requests")
def test_empty_cir_metadata_response():
    firestore_handler = FirestoreHandler()

    with pytest.raises(ValueError):
        firestore_handler.create_database_session()
        assert firestore_handler.latest_session_document_ref is None


@pytest.mark.usefixtures("mock_retrieve_latest_session")
def test_retrieve_latest_session():
    firestore_handler = FirestoreHandler()

    latest_session = firestore_handler.retrieve_latest_session()

    assert latest_session is not None
    assert latest_session == "abc-def-ghi"


@pytest.mark.usefixtures("mock_retrieve_latest_session_not_present")
def test_retrieve_latest_session_no_session():
    firestore_handler = FirestoreHandler()

    latest_session = firestore_handler.retrieve_latest_session()

    assert latest_session is None

@pytest.mark.usefixtures("mock_retrieve_latest_session_failure")
def test_retrieve_latest_session_failure():
    with pytest.raises(RetryError):
        firestore_handler = FirestoreHandler()
        latest_session = firestore_handler.retrieve_latest_session()
        assert latest_session is None


@pytest.mark.usefixtures("mock_document_reference")
def test_set_document_reference(mock_document_reference):
    firestore_handler = FirestoreHandler()

    firestore_handler.set_document_reference(mock_document_reference)

    assert firestore_handler.latest_session_document_ref is not None
    assert firestore_handler.latest_session_document_ref.id == "abc-def-ghi"
