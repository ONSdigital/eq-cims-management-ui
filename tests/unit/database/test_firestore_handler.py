from unittest.mock import MagicMock
from eq_cims_management_ui.utils.database.firestore_handler import FirestoreHandler

def test_create_session(monkeypatch):
    fake_client = MagicMock()
    fake_collection = MagicMock()
    fake_document = MagicMock()

    fake_client.collection.return_value = fake_collection
    fake_collection.document.return_value = fake_document

    fake_document.get.return_value = MagicMock(to_dict=lambda: {"created_at": "2020-01-01", "status": "Not started"})

    monkeypatch.setattr("google.cloud.firestore.Client", lambda: fake_client)

    firestore_handler = FirestoreHandler()

    document = firestore_handler.create()

    assert document.get().to_dict() == {"created_at": "2020-01-01", "status": "Not started"}





