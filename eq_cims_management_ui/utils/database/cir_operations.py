"""
This module contains functions for interacting with the CIR API.

Functions:
    check_cir_status
    get_ci_metadata

Raises:
    requests.exceptions.ConnectionError
    ValueError
"""

import logging
import os

import requests
from google.auth.transport.requests import Request
from google.oauth2 import id_token

logger = logging.getLogger(__name__)

CLIENT_ID = os.getenv("CLIENT_ID")


def make_authenticated_request(url: str) -> requests.Response:
    """
    Make an authenticated request to CIR using a token given it is protected by Identity-Aware Proxy.

    Args:
        url: The URL to which the authenticated GET request will be made.

    Returns:
        Response: The response object from the authenticated GET request.
    """
    open_id_connect_token = id_token.fetch_id_token(Request(), CLIENT_ID)  # type: ignore[no-untyped-call]

    headers = {"Authorization": f"Bearer {open_id_connect_token}"}

    return requests.get(url, headers=headers, timeout=15)


def check_cir_status() -> None:
    """
    Checks the availability of CIR by making a GET request to the '/status' endpoint of CIR API. If the request
    returns a non-200 status code, an exception is raised.

    Raises:
        HTTPError: If the response from CIR is not 200.
        requests.exceptions.ConnectionError: If the request returns a non-200 status code.
    """
    try:
        logger.info("Checking CIR status endpoint...")
        cir_status_url = f"{os.getenv("CIR_API_BASE_URL")}/status"
        status_response = (
            make_authenticated_request(cir_status_url) if CLIENT_ID else requests.get(cir_status_url, timeout=15)
        )
        if status_response.status_code == 200:
            logger.info("Successfully checked CIR status endpoint.")
        else:
            logger.error("Failed to check CIR status endpoint.")
            status_response.raise_for_status()

    except requests.exceptions.ConnectionError as error:
        logger.exception("Failed to connect to CIR.")
        raise requests.exceptions.ConnectionError from error


def get_ci_metadata() -> list[dict]:
    """
    Retrieves collection instrument metadata from CIR by making a GET request to the CIR API. The metadata is
    returned as a list of collection instrument metadata objects. If the response from CIR is empty, an exception
    is raised.

    Returns:
        ci_metadata: A list of collection instrument metadata to be added to the Firestore database.

    Raises:
        HTTPError: If the response from CIR is not 200.
        ValueError: If the response from CIR is empty.
        ConnectionError: If the request to CIR fails.
    """
    try:
        logger.info("Retrieving collection instrument metadata from CIR...")
        cir_metadata_url = f"{os.getenv("CIR_API_BASE_URL")}/collection-instruments/metadata"
        metadata_response = (
            make_authenticated_request(cir_metadata_url) if CLIENT_ID else requests.get(cir_metadata_url, timeout=15)
        )

        if metadata_response.status_code != 200:
            logger.error("Failed to retrieve collection instrument metadata from CIR.")
            metadata_response.raise_for_status()

        ci_metadata: list[dict] = metadata_response.json()

        return ci_metadata  # noqa: TRY300

    except requests.exceptions.ConnectionError as error:
        logger.exception("Failed to connect to CIR.")
        raise requests.exceptions.ConnectionError from error
