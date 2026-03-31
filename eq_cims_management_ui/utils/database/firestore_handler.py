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
        self.latest_session_document = None

    def create_session(self):
        """Creates a new session in the Firestore database with a unique session ID. Adds session data to the database,
        particularly the time of creation and status of the session.
        """
        session_id = str(uuid.uuid4())
        latest_session_document = self.client.collection("sessions").document(session_id)
        
        latest_session_document.set({
            "created_at": str(datetime.now()),
            "status": "Not started",
        })        
            
        self.latest_session_document = latest_session_document

    def read_latest_session(self):
        """Reads the latest session from the Firestore database, retrieving all the CIs alongside the relevant data.
        
        Returns:
            dict: The list of CIs from the database.
        """
        # TODO: Remove commented code (unused)
        # all_sessions_docs = self.client.collection("sessions").stream()
        # for session in all_sessions_docs:
        #     print(f"{session.id} => {session.to_dict()}")
        
        print(self.latest_session_document.get().to_dict())
        
        return self.latest_session_document.get().to_dict()

