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

from google.api_core.exceptions import RetryError
from google.api_core.retry import Retry
from google.cloud.firestore import Client
from google.cloud.firestore_v1 import Query
from google.cloud.firestore_v1.base_document import BaseDocumentReference

from eq_cims_management_ui.utils.database.cir_operations import (
    check_cir_status,
    get_ci_metadata,
)
from eq_cims_management_ui.utils.socketio import socketio

logger = logging.getLogger(__name__)


class FirestoreHandler:
    """
    Handles CRUD interactions with the Firestore database to allow CIs and user sessions to be managed.

    Methods:
        create_database_session
        retrieve_latest_session
        set_document_reference
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

        check_cir_status()
        ci_metadata = get_ci_metadata()

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
        socketio.emit("button_enable", namespace="/")
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
            query_results_list = (
                self.client.collection("sessions").order_by("created_at", direction=Query.DESCENDING).limit(1).get()
            )

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

    def close_connection(self) -> None:
        """Closes the connection to the Firestore database by deleting the client instance."""
        self.client.close()  # type: ignore[no-untyped-call]

    def update_ci_status(self, ci_guid: str, status: str) -> None:
        session = self.latest_session_document_ref
        session.collection("metadata").document(ci_guid).update({"status": status}, retry=Retry(timeout=15))
        logger.info(
            "Updated CI status in Firestore database for CI guid: %s to status: %s",
            session.collection("metadata").document(ci_guid).get().to_dict()["cir_id"],
            session.collection("metadata").document(ci_guid).get().to_dict()["status"],
        )

    def update_session_status(self, status: str) -> None:
        self.latest_session_document_ref.update({"status": status}, retry=Retry(timeout=15))
        logger.info(
            "Updated session status in Firestore database to status: %s",
            self.latest_session_document_ref.get().to_dict()["status"],
        )
