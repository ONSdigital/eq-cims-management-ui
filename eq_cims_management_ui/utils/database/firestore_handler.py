"""This module provides the FirestoreHandler class which is responsible for interacting with the Firestore database.

Classes:
    FirestoreHandler
"""

import os
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

from google.api_core.exceptions import RetryError
from google.api_core.retry import Retry
from google.cloud import firestore


class FirestoreHandler:
    """Handles CRUD interactions with the Firestore database to allow CIs and user sessions to be managed.

    Methods:
        create_session
        read_latest_session
    """

    def __init__(self):
        os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
        self.client = firestore.Client()

    def create_new_session(self):
        """Creates a new session in the Firestore database with a unique session ID. Adds session data to the database,
        particularly the time of creation and status of the session.
        """
        session_id = str(uuid.uuid4())
        latest_session_document = self.client.collection("sessions").document(session_id)

        try:
            latest_session_document.set(
                {
                    "created_at": str(datetime.now(ZoneInfo("Europe/London")).strftime("%Y-%m-%d %H:%M:%S.%s")),
                    "status": "Not started",
                },
                retry=Retry(timeout=15),
            )
        except RetryError as error:
            raise RetryError(cause=error, message="Failed to create session in Firestore database.")

        return latest_session_document
