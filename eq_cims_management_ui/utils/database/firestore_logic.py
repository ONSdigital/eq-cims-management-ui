"""
This module contains the business logic for interacting with the Firestore database.

Functions:
    create_new_session
"""

import logging

from flask import current_app

from eq_cims_management_ui.utils.database.firestore_handler import FirestoreHandler

logger = logging.getLogger(__name__)



def create_new_session() -> None:
    """
    Creates a new session in the Firestore database by calling the create_database_session
    method of the FirestoreHandler class.
    """
    firestore_handler = current_app.config["firestore_handler"]
    firestore_handler.create_database_session()

def get_session():
    firestore_handler = current_app.config["firestore_handler"]
    return firestore_handler.latest_session_document_ref
