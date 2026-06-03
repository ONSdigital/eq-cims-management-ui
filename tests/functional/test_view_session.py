"""This module contains the functional tests for the View Session feature of the CIMS Management UI."""

import re  # Uses Regex to ensure case sensitivity for tests
from pathlib import Path

import pytest
import requests
from playwright.sync_api import Page, expect

table_column_headers = ["Survey ID", "Form type", "CIR ID", "CIR version", "Validator version", "Status"]


@pytest.fixture()
def setup_cir():
    schema_path = Path(__file__).parent / "test_ci.json"
    with open(schema_path) as f:
        test_schema = json.load(f)

    requests.post(
        url="http://localhost:3030/collection-instruments",
        params={"guid": "abcd", "validator_version": "0.0.1", "ci_version": "1"},
        json=test_schema,
        timeout=15,
    )

    yield

    requests.delete(
        url="http://localhost:3030/collection-instruments",
        params={"survey_id": "123"},
        timeout=15,
    )


@pytest.mark.usefixtures("setup_cir")
def test_view_session_displays_content(page: Page):
    """Verify that opening the view session page displays the expected content."""
    page.goto("http://localhost:5100/view-session")

    for header in table_column_headers:
        expect(page.get_by_role("columnheader", name=re.compile(header))).to_be_visible()
