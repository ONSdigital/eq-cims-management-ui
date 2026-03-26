import os

import mock
from google.cloud import firestore
from datetime import datetime
import google.auth.credentials
import uuid

# TODO: Temporary - will be removed once implemented using live data
mock_ci_guid = str(uuid.uuid4())

class FirestoreHandler:
    def __init__(self):
        os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
        
        self.session_id = str(uuid.uuid4())
        self.client = firestore.Client()
        print("Firestore client created")

    def create_session(self):
        sessions_document = self.client.collection("sessions").document(self.session_id)
        cis_collection = sessions_document.collection("cis")
        
        sessions_document.set({
            "created_at": str(datetime.now()),
            "status": "Not started",
        })
        
        # TODO: Temporary mock data - will be removed once implemented using live data
        cis_collection.document(mock_ci_guid).set({
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
        sessions_document = self.client.collection("sessions").document(self.session_id)
        
        # TODO: Mock data - will be removed once implemented using live data
        all_cis_docs = sessions_document.collection("cis").stream()
        for ci in all_cis_docs:
            print(f"{ci.id} => {ci.to_dict()}")
        
        print(sessions_document.get().to_dict())
        return sessions_document.get().to_dict()

