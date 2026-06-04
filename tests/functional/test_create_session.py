"""This module contains the functional tests for the Create Session feature of the CIMS Management UI."""

import json
import re

import pytest
import requests
from playwright.sync_api import Page, expect

table_column_headers = ["Survey ID", "Form type", "CIR ID", "CIR version", "Validator version", "Status"]


@pytest.fixture()
def setup_cir():
    """Fixture to set up a CIR for testing purposes by adding a test collection instrument to CIR."""
    schema_path = "tests/functional/test_ci.json"
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


def test_render_initial_page(page: Page):
    """Verify that the initial page renders correctly."""
    page.goto("http://localhost:5100/")

    expect(page).to_have_title(re.compile(r"Collection Instrument Migration Service \(CIMS\)"))


@pytest.mark.usefixtures("setup_cir")
def test_create_session_displays_content(page: Page):
    """Verify that clicking the create session button displays the expected content after making a request to CIR."""
    page.goto("http://localhost:5100/")

    create_session_button = page.get_by_test_id("create-session-btn")

    create_session_button.click()

    expect(page.get_by_role("heading", name=re.compile(r"Collection instruments"))).to_be_visible()

    expect(page.get_by_role("table")).to_be_visible()
    expect(page.get_by_text("abcd")).to_be_visible()

    # Asserts that all column headers are visible in the table
    for header in table_column_headers:
        expect(page.get_by_role("columnheader", name=re.compile(header))).to_be_visible()
