"""This module provides the FirestoreHandler class which is responsible for interacting with the Firestore database.

Classes:
    FirestoreHandler
"""

import os

from google.cloud import firestore
from datetime import datetime
import uuid

# TODO: Temporary - will be removed once implemented using live data
mock_ci_guid = str(uuid.uuid4())

class FirestoreHandler:
    """Handles CRUD interactions with the Firestore database to allow CIs and user sessions to be managed.

    Methods:
        create_session
        read_latest_session
    """

    def __init__(self):
        os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
        self.session_id = str(uuid.uuid4())
        self.client = firestore.Client()

        self.sessions_document = self.client.collection("sessions").document(self.session_id)
        self.cis_collection = self.sessions_document.collection("cis")

    def create_session(self):
        """Creates a new session in the Firestore database with a unique session ID. Adds session data to the database,
        particularly the time of creation and status of the session.
        """
        self.sessions_document.set({
            "created_at": str(datetime.now()),
            "status": "Not started",
        })

        # TODO: Temporary mock data - will be removed once implemented using live data
        self.cis_collection.document(mock_ci_guid).set({
            "guid": mock_ci_guid,
            "ci_version": 1,
            "validator_version": "1.0.0",
            "survey_id": "123",
            "form_type": "1234",
            "publish_date": str(datetime.now()),
            "status": "Not started",
            "error_message": None
            })

    def read_latest_session(self):
        """Reads the latest session from the Firestore database, retrieving all the CIs alongside the relevant data.

        Returns:
            dict: The list of CIs from the database.
        """
        # TODO: Mock data - will be removed once implemented using live data
        all_cis_docs = self.sessions_document.collection("cis").stream()
        for ci in all_cis_docs:
            print(f"{ci.id} => {ci.to_dict()}")

        print(self.sessions_document.get().to_dict())
        return self.sessions_document.get().to_dict()

