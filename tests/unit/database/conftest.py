import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_firestore_client(monkeypatch):
    mock_client = MagicMock()
    mock_collection = MagicMock()
    mock_document = MagicMock()

    mock_client.collection.return_value = mock_collection
    mock_collection.document.return_value = mock_document

    mock_document.get.return_value = MagicMock(to_dict=lambda: {"created_at": "2020-01-01", "status": "Not started"})

    monkeypatch.setattr("google.cloud.firestore.Client", lambda: mock_client)