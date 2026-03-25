import os

import mock
from google.cloud import firestore
import google.auth.credentials

class FirestoreClient: ## Might need to rename this as it's also named after Google Library

    def __init__(self):
        os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
        credentials = mock.Mock(spec=google.auth.credentials.Credentials)
        self.client = firestore.Client(credentials=credentials)
        print("Firestore client created")

    def create_session(self):
        document = self.client.collection("test").document("session_id")
        document.set({"session_id": "12345"})
        print("Added data to firestore")

    def get_session(self):
        document = self.client.collection("test").document("session_id")
        print(document.get().to_dict())
        return document.get().to_dict()

