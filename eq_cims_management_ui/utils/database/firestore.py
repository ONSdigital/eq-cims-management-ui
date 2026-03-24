import mock
from google.cloud import firestore
import google.auth.credentials


class FirestoreClient:
    def __init__(self):
        credentials = mock.Mock(spec=google.auth.credentials.Credentials)
        self.client = firestore.Client(credentials=credentials)
    
    def create_session(self):
        session = {
            "id": "1",
        }
