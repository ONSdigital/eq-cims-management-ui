#!/usr/bin/env python
import os
import random
import secrets
import string
import uuid

import requests
from structlog import get_logger

logger = get_logger()

guids = [str(uuid.uuid4()) for _ in range(5)]
survey_ids = random.sample(range(100, 999), 5)

url = f"{os.getenv("CIR_API_BASE_URL")}/collection-instruments"
headers = {"accept": "application/json", "Content-Type": "application/json"}

for i, guid in enumerate(guids):
    params = {"guid": guid, "validator_version": "0.0.1", "ci_version": "1"}
    payload = {
        "data_version": "string",
        "language": "string",
        "survey_id": str(survey_ids[i]),
        "title": "string",
        "form_type": "".join(secrets.choice(string.ascii_lowercase) for _ in range(4)),
        "legal_basis": "",
        "metadata": ["string"],
        "mime_type": "",
        "navigation": {"additionalProp1": {}},
        "questionnaire_flow": {"additionalProp1": {}},
        "post_submission": {"additionalProp1": {}},
        "sds_schema": "",
        "sections": ["string"],
        "submission": {"additionalProp1": {}},
        "theme": "",
    }

    response = requests.post(url, params=params, headers=headers, json=payload, timeout=10)
    logger.info("GUID: %s | Survey ID: %s | Status: %s", guid, survey_ids[i], response.status_code)
    logger.info("Response: %s", response.json())
