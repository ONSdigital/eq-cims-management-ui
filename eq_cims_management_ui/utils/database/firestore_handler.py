"""
This module provides the FirestoreHandler class which is responsible for interacting with the Firestore database.

Classes:
    FirestoreHandler

Raises:
    RetryError
"""

import logging
import uuid
from datetime import datetime, timezone

from google.api_core.exceptions import RetryError
from google.api_core.retry import Retry
from google.cloud.firestore import Client
from google.cloud.firestore_v1.base_document import BaseDocumentReference

logger = logging.getLogger(__name__)


# pylint: disable=too-few-public-methods
class FirestoreHandler:
    """
    Handles CRUD interactions with the Firestore database to allow CIs and user sessions to be managed.

    Methods:
        create_database_session
    """

    def __init__(self) -> None:
        self.client: Client = Client()
        self.latest_session_document_ref: BaseDocumentReference | None = None

    def create_database_session(self) -> None:
        """
        Creates a new session in the Firestore database with a unique session ID. Adds session data to the database,
        particularly the time of creation and status of the session.
        """
        session_id = str(uuid.uuid4())
        latest_session_document_ref = self.client.collection("sessions").document(session_id)

        try:
            logger.info("Creating session in Firestore database...")
            latest_session_document_ref.set(
                {
                    "created_at": datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%s"),
                    "status": "Not started",
                },
                retry=Retry(timeout=15),
            )
        except RetryError as error:
            logger.exception("Failed to create session in Firestore database.")
            raise RetryError(
                cause=error,
                message="Failed to create session in Firestore database.",
            ) from error  # type: ignore[no-untyped-call]

        logger.info("Session created successfully: %s", session_id)
        self.latest_session_document_ref = latest_session_document_ref
