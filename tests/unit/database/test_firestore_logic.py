"""This module contains tests for the firestore_logic module to ensure business logic is working as expected."""

import pytest

from eq_cims_management_ui.utils.database.firestore_logic import create_new_session


@pytest.mark.usefixtures("mock_client", "mock_create_database_session")
def test_create_session(mock_client, mock_create_database_session):
    """Test that the create_new_session function calls the correct methods from the FirestoreHandler class."""
    create_new_session()

    assert mock_client.call_count == 1
    assert mock_create_database_session.return_value is not None
    assert mock_create_database_session.call_count == 1
