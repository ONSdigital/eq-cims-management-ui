import pytest

from eq_cims_management_ui.utils.database.firestore_handler import FirestoreHandler

@pytest.mark.usefixtures("mock_firestore_client")
def test_create_session():
    firestore_handler = FirestoreHandler()

    firestore_handler.create_session()

    assert firestore_handler.latest_session_document.get().to_dict() == {"created_at": "2020-01-01", "status": "Not started"}





