import os

import mock
from google.cloud import firestore
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
        document = self.client.collection("sessions").document(self.session_id)
        document.set({"session_id": self.session_id})
        print("Added data to firestore")
    
    # Temporary method    
    def get_all_sessions(self):
        session_docs = self.client.collection("sessions").stream()

        for session in session_docs:
            print(f"{session.id} => {session.to_dict()}")

    def get_session(self):
        document = self.client.collection("sessions").document(self.session_id)
        print(document.get().to_dict())
        return document.get().to_dict()

