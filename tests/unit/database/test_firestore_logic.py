"""This module contains tests for the firestore_logic module to ensure business logic is working as expected."""

from unittest import mock

from eq_cims_management_ui.utils.database.firestore_logic import create_session


@mock.patch("eq_cims_management_ui.utils.database.firestore_logic.FirestoreHandler.create_new_session")
def test_create_session(mock_create_new_session):
    """Test that the create_session function calls the correct methods from the FirestoreHandler class."""
    create_session()

    assert mock_create_new_session.return_value is not None
    assert mock_create_new_session.call_count == 1
