import pytest
from unittest.mock import MagicMock, patch, Mock


# import eq_cims_management_ui.utils.database.firestore_handler as fh_mod
#
#
# @pytest.fixture
# def mock_firestore_client(mocker):
#     """Return a MagicMock that behaves like a Firestore client and patch the
#     firestore.Client used in the FirestoreHandler module.
#
#     The mock provides:
#     - client.collection(name).document(id).set(data)
#     - client.collection(name).document(id).get().to_dict() -> dict
#     - client.collection(name).stream() -> iterable (empty list by default)
#     """
#     # Mock a document snapshot (what .get() returns)
#     doc_snapshot = MagicMock()
#     doc_snapshot.to_dict.return_value = {"created_at": "2020-01-01", "status": "Not started"}
#
#     # Mock document reference with set and get
#     mock_document = MagicMock()
#     mock_document.set.return_value = None
#     mock_document.get.return_value = doc_snapshot
#
#     # Mock collection which can return documents and stream
#     mock_collection = MagicMock()
#     mock_collection.document.return_value = mock_document
#     mock_collection.stream.return_value = []
#
#     # Mock client which returns the mock collection
#     mock_client = MagicMock()
#     mock_client.collection.return_value = mock_collection
#
#     # Patch the firestore.Client used inside the firestore_handler module to return our mock_client
#     mocker.patch.object(fh_mod.firestore, "Client", return_value=mock_client)
#
#     return mock_client

@pytest.fixture
def mock_firestore_client():
    with patch("google.cloud.firestore.Client") as mock_client:
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        yield mock_instance
