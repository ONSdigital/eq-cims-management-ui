"""This module contains the functional tests for the Create Session feature of the CIMS Management UI."""

import re  # Uses Regex to ensure case sensitivity for tests

from playwright.sync_api import Page, Route, expect

table_column_headers = ["Survey ID", "Form type", "CIR ID", "CIR version", "Validator version", "Status"]


def test_render_initial_page(page: Page):
    """Verify that the initial page renders correctly."""
    page.goto("http://localhost:5100/")

    expect(page).to_have_title(re.compile(r"Collection Instrument Migration Service \(CIMS\)"))


def test_create_session_displays_content(page: Page):
    """Verify that clicking the create session button displays the expected content."""

    def handle_status(route: Route):
        route.fulfill(json={"status": "OK"})

    def handle_ci_json(route: Route):
        ci_json = [
            {
                "ci_version": 1,
                "data_version": "0.0.1",
                "validator_version": "0.0.1",
                "classifier_type": "form_type",
                "classifier_value": "1234",
                "guid": "abcd",
                "language": "en",
                "published_at": "2026-01-01T00:00:00.00Z",
                "survey_id": "000",
                "title": "Test Survey",
            },
        ]

        route.fulfill(json=ci_json)

    page.route("**/status", handle_status)
    page.route("**/collection-instruments/metadata", handle_ci_json)

    page.goto("http://localhost:5100/")

    create_session_button = page.get_by_test_id("create-session-btn")

    create_session_button.click()

    expect(page.get_by_role("heading", name=re.compile(r"Collection instruments"))).to_be_visible()

    expect(page.get_by_role("table")).to_be_visible()
    expect(page.get_by_text("abcd")).to_be_visible()

    # Asserts that all column headers are visible in the table
    for header in table_column_headers:
        expect(page.get_by_role("columnheader", name=re.compile(header))).to_be_visible()
