from google.cloud.firestore_v1.base_document import BaseDocumentReference

from eq_cims_management_ui.utils.database.firestore_handler import FirestoreHandler


def create_session() -> BaseDocumentReference:
    firestore_handler = FirestoreHandler()

    return firestore_handler.create_new_session()
