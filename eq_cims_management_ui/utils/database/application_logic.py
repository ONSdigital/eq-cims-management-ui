"""
This module contains the business logic for interacting with the Firestore database.

Functions:
    create_new_session
    get_collection_instruments
    is_latest_session_present
"""

import logging

from flask import g
from google.api_core.exceptions import RetryError

from eq_cims_management_ui.utils.database.status import Status

logger = logging.getLogger(__name__)


def create_new_session() -> None:
    """
    Creates a new session in the Firestore database by calling the create_database_session
    method of the FirestoreHandler class.
    """
    firestore_handler = g.firestore_handler
    firestore_handler.create_database_session()


def get_collection_instruments() -> list[dict]:
    """
    Iterates through the collection instruments in the latest session in the Firestore database, which
    will be used when displaying a list of CIs to the user.

    Returns:
        list[dict]: A list of the metadata of the collection instruments in the latest session.

    Raises:
        RetryError: If the Firestore operation fails
    """
    try:
        firestore_handler = g.firestore_handler
        latest_session = firestore_handler.latest_session_document_ref
        ci_metadata_documents = latest_session.collection("metadata").stream()

        return [metadata_item.to_dict() for metadata_item in ci_metadata_documents]
    except RetryError as error:
        logger.exception("Failed to retrieve collection instruments from Firestore after multiple attempts.")
        raise RetryError(
            cause=error,
            message="Failed to create session in Firestore database.",
        ) from error  # type: ignore[no-untyped-call]


def is_latest_session_present() -> bool:
    """
    Checks if there is a session present in the Firestore database and that its status is not "Not started".

    Returns:
        bool: True if there is a session present with its status as not "Not started", False otherwise.
    """
    firestore_handler = g.firestore_handler

    if session_doc_ref := firestore_handler.retrieve_latest_session():
        current_session = session_doc_ref.get().to_dict()

        if current_session["status"] != Status.NOT_STARTED.value:
            firestore_handler.set_document_reference(session_doc_ref)
            return True
        return False

    return False
