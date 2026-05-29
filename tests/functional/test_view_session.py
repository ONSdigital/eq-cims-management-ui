"""This module contains the functional tests for the View Session feature of the CIMS Management UI."""

import re  # Uses Regex to ensure case sensitivity for tests

from playwright.sync_api import Page, expect

table_column_headers = ["Survey ID", "Form type", "CIR ID", "CIR version", "Validator version", "Status"]


def test_view_session_displays_content(page: Page):
    """Verify that opening the view session page displays the expected content."""
    page.goto("http://localhost:5100/view-session")

    for header in table_column_headers:
        expect(page.get_by_role("columnheader", name=re.compile(header))).to_be_visible()
