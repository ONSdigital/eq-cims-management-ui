"""This module contains tests for the FirestoreHandler class to ensure interactions with Firestore instances
are working as expected.
"""

import pytest
from google.api_core.exceptions import RetryError

from eq_cims_management_ui.utils.database.firestore_handler import FirestoreHandler


@pytest.mark.usefixtures("mock_firestore_client")
def test_create_session():
    """Test that a new session document is created in a mock Firestore instance with the expected
    data when the create_new_session method is called.
    """
    firestore_handler = FirestoreHandler()

    session_document = firestore_handler.create_new_session()

    assert session_document.get().to_dict() == {
        "created_at": "2026-04-02 12:17:04.1775128624",
        "status": "Not started",
    }


@pytest.mark.usefixtures("mock_erroneous_firestore_client")
def test_create_session_fails():
    """Test that an exception is raised when the create_new_session method fails to create a new
    session given an erroneous Firestore instance.
    """
    firestore_handler = FirestoreHandler()

    with pytest.raises(RetryError):
        session_document = firestore_handler.create_new_session()
        assert session_document is None
