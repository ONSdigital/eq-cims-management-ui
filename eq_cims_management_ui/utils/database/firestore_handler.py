"""
This module provides the FirestoreHandler class which is responsible for interacting with the Firestore database.

Classes:
    FirestoreHandler

Raises:
    RetryError
    requests.exceptions.ConnectionError
    ValueError
"""

import logging
import os
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
from google.api_core.exceptions import RetryError
from google.api_core.retry import Retry
from google.cloud.firestore import Client
from google.cloud.firestore_v1 import Query
from google.cloud.firestore_v1.base_document import BaseDocumentReference

logger = logging.getLogger(__name__)


class FirestoreHandler:
    """
    Handles CRUD interactions with the Firestore database to allow CIs and user sessions to be managed.

    Methods:
        create_database_session
        retrieve_latest_session
        set_document_reference
        check_cir_status
        get_ci_metadata
    """

    def __init__(self) -> None:
        self.client: Client = Client()
        self.latest_session_document_ref: BaseDocumentReference | None = None

    def create_database_session(self) -> None:
        """
        Creates a new session in the Firestore database with a unique session ID. Adds session data to the database,
        particularly the time of creation and status of the session. Additionally, retrieves collection instruments from
        CIR and adds them to the database.
        """
        session_id = str(uuid.uuid4())
        latest_session_document_ref = self.client.collection("sessions").document(session_id)

        self.check_cir_status()
        ci_metadata = self.get_ci_metadata()

        try:
            logger.info("Creating session in Firestore database...")
            latest_session_document_ref.set(
                {
                    "created_at": datetime.now(ZoneInfo("Europe/London")).isoformat(),
                    "status": "Not started",
                },
                retry=Retry(timeout=15),
            )

            for ci_metadata_item in ci_metadata:
                latest_session_document_ref.collection("metadata").document(ci_metadata_item["guid"]).set(
                    {
                        "survey_id": ci_metadata_item["survey_id"],
                        "form_type": ci_metadata_item["classifier_value"],
                        "cir_id": ci_metadata_item["guid"],
                        "cir_version": ci_metadata_item["ci_version"],
                        "validator_version": ci_metadata_item["validator_version"],
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

    def retrieve_latest_session(self) -> BaseDocumentReference | None:
        """
        Queries the Firestore database for the latest session by sorting all session by creation date in descending
        order.

        Returns:
            BaseDocumentReference: The document reference of the latest session found.
            None: If no session is found.
        """
        try:
            latest_document_query = (
                self.client.collection("sessions").order_by("created_at", direction=Query.DESCENDING).limit(1)
            )

            query_results_list = latest_document_query.get()

            # Get the latest session document reference by selecting the first item of the resulting list from the query
            if len(query_results_list) > 0:
                return query_results_list[0].reference
        except RetryError as error:
            logger.exception("Failed to retrieve latest session from Firestore database.")
            raise RetryError(
                cause=error,
                message="Failed to retrieve session in Firestore database.",
            ) from error  # type: ignore[no-untyped-call]

        return None

    def set_document_reference(self, document_reference: BaseDocumentReference) -> None:
        """
        Set the latest session document reference. Used when an in-progress session is present and setting this
        reference as an attribute of the FirestoreHandler instance.

        Args:
            document_reference: The document reference of the latest session found.
        """
        self.latest_session_document_ref = document_reference

    @staticmethod
    def check_cir_status():
        """
        Checks the availability of CIR by making a GET request to the '/status' endpoint of CIR API. If the request
        returns a non-200 status code, an exception is raised.

        Raises:
            requests.exceptions.ConnectionError: If the request returns a non-200 status code.
        """
        try:
            logger.info("Checking CIR status endpoint...")
            cir_status_url = f"http://{os.getenv("CIR_API_BASE_URL")}/status"
            status = requests.get(cir_status_url, timeout=15)
            if status.status_code == 200:
                logger.info("Successfully checked CIR status endpoint.")

        except requests.exceptions.ConnectionError as error:
            logger.exception("Failed to connect to CIR.")
            raise requests.exceptions.ConnectionError from error

    @staticmethod
    def get_ci_metadata() -> list[dict]:
        """
        Retrieves collection instrument metadata from CIR by making a GET request to the CIR API. The metadata is
        returned as a list of collection instrument metadata objects. If the response from CIR is empty, an exception
        is raised.

        Returns:
            ci_metadata: A list of collection instrument metadata to be added to the Firestore database.

        Raises:
            ValueError: If the response from CIR is empty.
        """
        logger.info("Retrieving collection instrument metadata from CIR...")
        cir_metadata_url = f"http://{os.getenv("CIR_API_BASE_URL")}/collection-instruments/metadata"
        metadata_received = requests.get(cir_metadata_url, timeout=15)
        ci_metadata = metadata_received.json()

        if not isinstance(ci_metadata, list) and ci_metadata.get("message") == "No CI found":
            logger.error("Failed to retrieve collection instrument metadata from CIR.")
            raise ValueError

        return ci_metadata
