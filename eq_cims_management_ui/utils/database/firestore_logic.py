"""
This module contains the business logic for interacting with the Firestore database.

Functions:
    create_session
"""

from google.cloud.firestore_v1.base_document import BaseDocumentReference

from eq_cims_management_ui.utils.database.firestore_handler import FirestoreHandler


def create_session() -> BaseDocumentReference:
    """
    Creates a new session in the Firestore database.

    Returns:
        BaseDocumentReference: A reference to the created session document.
    """
    firestore_handler = FirestoreHandler()

    return firestore_handler.create_new_session()
