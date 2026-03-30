"""This module provides the FirestoreHandler class which is responsible for interacting with the Firestore database.

Classes:
    FirestoreHandler
"""

import os

from google.cloud import firestore
from datetime import datetime
import uuid

class FirestoreHandler:
    """Handles CRUD interactions with the Firestore database to allow CIs and user sessions to be managed.

    Methods:
        create_session
        read_latest_session
    """

    def __init__(self):
        os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
        self.client = firestore.Client()

    def create_session(self):
        """Creates a new session in the Firestore database with a unique session ID. Adds session data to the database,
        particularly the time of creation and status of the session.
        """
        session_id = str(uuid.uuid4())
        sessions_document = self.client.collection("sessions").document(session_id)
        
        sessions_document.set({
            "created_at": str(datetime.now()),
            "status": "Not started",
        })        
            
        return sessions_document

    def read_latest_session(self, sessions_document):
        """Reads the latest session from the Firestore database, retrieving all the CIs alongside the relevant data.
        
        Returns:
            dict: The list of CIs from the database.
        """
        print(sessions_document.get().to_dict())
        return sessions_document.get().to_dict()

