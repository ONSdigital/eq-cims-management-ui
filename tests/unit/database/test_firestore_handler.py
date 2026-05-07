"""
This module contains tests for the FirestoreHandler class to ensure interactions with Firestore instances
are working as expected.
"""

import pytest
from google.api_core.exceptions import RetryError

from eq_cims_management_ui.utils.database.firestore_handler import FirestoreHandler


@pytest.mark.usefixtures("mock_firestore_session")
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


@pytest.mark.usefixtures("mock_erroneous_firestore_session")
def test_create_session_fails():
    """
    Test that an exception is raised when the create_database_session method fails to create a new
    session given an erroneous Firestore instance.
    """
    firestore_handler = FirestoreHandler()

    with pytest.raises(RetryError):
        firestore_handler.create_database_session()
        assert firestore_handler.latest_session_document_ref is None
