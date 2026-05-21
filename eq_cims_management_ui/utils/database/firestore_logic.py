"""
This module contains the business logic for interacting with the Firestore database.

Functions:
    create_new_session
"""

import logging

from flask import current_app
from requests.exceptions import RetryError

logger = logging.getLogger(__name__)


def create_new_session() -> None:
    """
    Creates a new session in the Firestore database by calling the create_database_session
    method of the FirestoreHandler class.
    """
    firestore_handler = current_app.config["firestore_handler"]
    firestore_handler.create_database_session()


def get_collection_instruments() -> list[dict]:
    try:
        firestore_handler = current_app.config["firestore_handler"]
        latest_session = firestore_handler.latest_session_document_ref
        ci_metadata_documents = latest_session.collection("metadata").stream()

        return [metadata_item.to_dict() for metadata_item in ci_metadata_documents]
    except RetryError as error:
        logger.exception("Failed to retrieve collection instruments from Firestore after multiple attempts.")
        raise RetryError from error


def is_latest_session_present() -> bool:
    firestore_handler = current_app.config["firestore_handler"]

    if session_doc_ref := firestore_handler.retrieve_latest_session():
        current_session = session_doc_ref.get().to_dict()

        if current_session["status"] != "Not started":  # TO BECOME AN ENUM
            firestore_handler.set_document_reference(session_doc_ref)
            return True
        return False

    return False
