"""This module contains tests for the firestore_logic module to ensure business logic is working as expected."""

import pytest

from eq_cims_management_ui.utils.database.firestore_logic import create_session


@pytest.mark.usefixtures("mock_firestore_client")
def test_create_session():
    session = create_session()

    assert session.get().to_dict() == {
        "created_at": "2026-04-02 12:17:04.1775128624",
        "status": "Not started",
    }
