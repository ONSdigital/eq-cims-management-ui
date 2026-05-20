"""
This module provides the FirestoreHandler class which is responsible for interacting with the Firestore database.

Classes:
    FirestoreHandler

Raises:
    RetryError
"""

import logging
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
from google.api_core.exceptions import RetryError
from google.api_core.retry import Retry
from google.cloud.firestore import Client
from google.cloud.firestore_v1.base_document import BaseDocumentReference
from google.cloud.firestore_v1 import Query

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
            status = requests.get("http://localhost:3030/status")
            if status.status_code == 200:
                logger.info("Successfully checked CIR status endpoint.")

        except requests.exceptions.ConnectionError:
            logger.exception("Failed to connect to CIR.")
            raise ConnectionError

        try:
            logger.info("Creating session in Firestore database...")
            latest_session_document_ref.set(
                {
                    "created_at": datetime.now(ZoneInfo("Europe/London")).isoformat(),
                    "status": "Not started",
                },
                retry=Retry(timeout=15),
            )

            metadata_received = requests.get("http://localhost:3030/v2/collection-instruments/metadata")
            ci_metadata = metadata_received.json()
            if type(ci_metadata) is not list and ci_metadata.get("message") == "No CI found":
                logger.error("Failed to retrieve collection instrument metadata from CIR.")
                raise ValueError("Failed to retrieve collection instrument metadata from CIR.")

            for ci_metadata_item in ci_metadata:
                latest_session_document_ref.collection("metadata").document(ci_metadata_item["guid"]).set(
                    {
                        "survey_id": ci_metadata_item["survey_id"],
                        "form_type": ci_metadata_item["classifier_value"],
                        "cir_id": ci_metadata_item["guid"],
                        "cir_version": ci_metadata_item["ci_version"],
                        "validator_version": ci_metadata_item["validator_version"],
                        "status": "Not started"
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

    def set_document_reference(self, document_reference: BaseDocumentReference):
        self.latest_session_document_ref = document_reference

    def retrieve_latest_session(self):
        ## Go into database, check for session status and return CIs from there
        latest_document_query = self.client.collection("sessions").order_by(
            "created_at",
            direction=Query.DESCENDING
        ).limit(1)

        query_results_list = latest_document_query.get()

        # Get the latest session document by retrieving the first element from the query result which is a list
        if len(query_results_list) > 0:
            return query_results_list[0].reference
        return None
