from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_firestore_client(monkeypatch):
    mock_client = MagicMock()
    mock_collection = MagicMock()
    mock_document = MagicMock()

    mock_client.collection.return_value = mock_collection
    mock_collection.document.return_value = mock_document

    mock_document.get.return_value = MagicMock(to_dict=lambda: {'status': 'Not started', 'created_at': '2026-04-02 12:17:04.1775128624'})

    monkeypatch.setattr("google.cloud.firestore.Client", lambda: mock_client)
