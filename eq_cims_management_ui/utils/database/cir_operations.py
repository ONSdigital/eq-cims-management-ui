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

logger = logging.getLogger(__name__)


def check_cir_status() -> None:
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

    # CI metadata is always returned as a list of dictionaries given CIs are published
    if not isinstance(ci_metadata, list) or ci_metadata[0].get("message") == "No CI found":
        logger.error("Failed to retrieve collection instrument metadata from CIR.")
        raise ValueError

    return ci_metadata
