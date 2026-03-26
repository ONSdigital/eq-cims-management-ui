import os

import mock
from google.cloud import firestore
from datetime import datetime
import google.auth.credentials
import uuid

class FirestoreClient: ## Might need to rename this as it's also named after Google Library

    def __init__(self):
        os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
        credentials = mock.Mock(spec=google.auth.credentials.Credentials)
        self.session_id = str(uuid.uuid4())
        self.client = firestore.Client(credentials=credentials)
        print("Firestore client created")

    def create_session(self):
        sessions_document = self.client.collection("sessions").document(self.session_id)
        cis_collection = sessions_document.collection("cis")
        
        sessions_document.set({
            "created_at": str(datetime.now()),
            "status": "Not started",
        })
        
        cis_collection.document("list_of_cis").set({
            "guid": str(uuid.uuid4()), 
            "ci_version": 1,
            "validator_version": "1.0.0",
            "survey_id": "123",
            "form_type": "1234",
            "publish_date": str(datetime.now()),
            "status": "Not started",
            "error_message": None
            })
        print("Added data to firestore")
    
    # Temporary method    
    def get_all_sessions(self):
        session_docs = self.client.collection("sessions").stream()

        for session in session_docs:
            print(f"{session.id} => {session.to_dict()}")

    def get_session(self):
        sessions_document = self.client.collection("sessions").document(self.session_id)
        cis_document = sessions_document.collection("cis").document("list_of_cis")
        
        print(sessions_document.get().to_dict())
        print(cis_document.get().to_dict())
        return sessions_document.get().to_dict()

