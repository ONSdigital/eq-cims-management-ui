"""
This module contains the business logic for interacting with the Firestore database.

Functions:
    create_new_session
    get_collection_instruments
    is_latest_session_present
"""

import logging

from flask import g, current_app
from google.api_core.exceptions import RetryError

from eq_cims_management_ui.utils.database.status import Status

logger = logging.getLogger(__name__)


def create_new_session() -> None:
    """
    Creates a new session in the Firestore database by calling the create_database_session
    method of the FirestoreHandler class.
    """
    firestore_handler = current_app.config["firestore_handler"]
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
        firestore_handler = current_app.config["firestore_handler"]
        latest_session = firestore_handler.latest_session_document_ref
        ci_metadata_documents = latest_session.collection("metadata").stream()

        return [metadata_item.to_dict() for metadata_item in ci_metadata_documents]
    except RetryError as error:
        logger.exception("Failed to retrieve collection instruments from Firestore after multiple attempts.")
        raise RetryError(
            cause=error,
            message="Failed to create session in Firestore database.",
        ) from error  # type: ignore[no-untyped-call]

def get_session_status() -> str | None:
    """
    Retrieves the status of the latest session in the Firestore database.

    Returns:
        str: The status of the latest session.
    """
    firestore_handler = current_app.config["firestore_handler"]

    if session_doc_ref := firestore_handler.retrieve_latest_session():
        current_session = session_doc_ref.get().to_dict()
        return current_session["status"]

    return None

def is_latest_session_in_progress() -> bool:
    """
    Checks if there is a session in progress in the Firestore database and that its status is not "Not started" or "Success".

    Returns:
        bool: True if there is a session in progress with its status as not "Not started" or "Success", False otherwise.
    """
    firestore_handler = current_app.config["firestore_handler"]

    if session_doc_ref := firestore_handler.retrieve_latest_session():
        current_session = session_doc_ref.get().to_dict()

        if current_session["status"] == Status.RUNNING.value or current_session["status"] == Status.FAILURE.value:
            firestore_handler.set_document_reference(session_doc_ref)
            return True
        return False

    return False

def update_ci_status(guid, status) -> None:
    firestore_handler = current_app.config["firestore_handler"]
    firestore_handler.update_ci_status(guid, status)

def update_session_status(status) -> None:
    firestore_handler = current_app.config["firestore_handler"]
    firestore_handler.update_session_status(status)
