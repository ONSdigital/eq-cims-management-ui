"""
This module contains the business logic for interacting with the Firestore database.

Functions:
    create_new_session
"""

import logging

from flask import current_app

logger = logging.getLogger(__name__)



def create_new_session() -> None:
    """
    Creates a new session in the Firestore database by calling the create_database_session
    method of the FirestoreHandler class.
    """
    firestore_handler = current_app.config["firestore_handler"]
    firestore_handler.create_database_session()


def get_collection_instruments():
    try:
        firestore_handler = current_app.config["firestore_handler"]
        latest_session = firestore_handler.latest_session_document_ref
        ci_metadata_documents = latest_session.collection("metadata").stream()
        ci_metadata = []
        for metadata_item in ci_metadata_documents:
            ci_metadata.append(metadata_item.to_dict())
        return ci_metadata
    except Exception:
        # Retrieve the existing latest session
        # Need an instance of firestore handler class with the latest session document reference set
        pass

def is_latest_session_present():
    firestore_handler = current_app.config["firestore_handler"]

    if session_doc_ref := firestore_handler.retrieve_latest_session():

        current_session = session_doc_ref.get().to_dict()

        if current_session["status"] != "Not started": # TO BECOME AN ENUM
            firestore_handler.set_document_reference(session_doc_ref)
            return True
        return False

    else:
        return False
