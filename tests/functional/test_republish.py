"""This module contains the functional tests for the Republish feature of the CIMS Management UI."""

import json
import re

import pytest
import requests
from playwright.sync_api import Page, expect

table_column_headers = ["Survey ID", "Form type", "CIR ID", "CIR version", "Validator version", "Status"]


@pytest.fixture()
def setup_cir():
    """Fixture to set up a CIR for testing purposes by adding test collection instruments to CIR."""
    schema_path = "tests/functional/test_ci.json"
    with open(schema_path, encoding="utf-8") as f:
        test_schema = json.load(f)

    requests.post(
        url="http://localhost:3030/collection-instruments",
        params={"guid": "75f9d538-dda2-4852-ab6d-729391da2cdc", "validator_version": "0.0.1", "ci_version": "2"},
        json=test_schema,
        timeout=15,
    )

    requests.post(
        url="http://localhost:3030/collection-instruments",
        params={"guid": "35ef7238-d689-4285-adee-bd662a051f83", "validator_version": "0.0.1", "ci_version": "3"},
        json=test_schema,
        timeout=15,
    )

    requests.post(
        url="http://localhost:3030/collection-instruments",
        params={"guid": "cccac6bb-82de-4eca-9cee-6ca59b2751db", "validator_version": "0.0.1", "ci_version": "4"},
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


def test_no_cis_present(page: Page):
    """
    Verify that clicking the create session button displays an error message when no collection instruments
    are present in CIR.
    """
    page.goto("http://localhost:5100/")

    create_session_button = page.get_by_test_id("create-session-btn")

    create_session_button.click()

    expect(page.get_by_role("heading", name=re.compile(r"Sorry, there is a problem with the service"))).to_be_visible()


@pytest.mark.usefixtures("setup_cir")
def test_display_content(page: Page):
    """
    Verify that clicking the create session button displays the expected content after making a request to CIR. Verify
    that the republish button is disabled until the republish process is complete. Verify that the statuses of the CIs
    are displayed correctly before and after the republish process.
    """
    page.goto("http://localhost:5100/")

    create_session_button = page.get_by_test_id("create-session-btn")

    create_session_button.click()

    expect(page.get_by_role("heading", name=re.compile(r"Collection instruments"))).to_be_visible()

    expect(page.get_by_role("table")).to_be_visible()
    expect(page.get_by_text("75f9d538-dda2-4852-ab6d-729391da2cdc")).to_be_visible()
    expect(page.get_by_text("35ef7238-d689-4285-adee-bd662a051f83")).to_be_visible()
    expect(page.get_by_text("cccac6bb-82de-4eca-9cee-6ca59b2751db")).to_be_visible()

    # Asserts that all column headers are visible in the table
    for header in table_column_headers:
        expect(page.get_by_role("columnheader", name=re.compile(header))).to_be_visible()

    republish_button = page.get_by_test_id("republish-btn")

    expect(page.get_by_text("Not started")).to_have_count(3)

    republish_button.click()
    expect(republish_button).to_be_disabled()

    expect(page.get_by_text("Success")).to_have_count(3, timeout=15000)
    expect(republish_button).to_be_disabled()


@pytest.mark.usefixtures("setup_cir")
def test_display_content_after_republish_in_progress(page: Page):
    """
    Verify that clicking the back button after a successful republish process returns the user to the create session
    page.
    """
    page.goto("http://localhost:5100/")

    create_session_button = page.get_by_test_id("create-session-btn")

    create_session_button.click()

    republish_button = page.get_by_test_id("republish-btn")
    republish_button.click()

    expect(republish_button).to_be_visible()

    page.wait_for_timeout(3000)

    expect(republish_button).to_be_disabled()
    expect(page.get_by_text("Started")).to_have_count(1)

    expect(page.get_by_text("Success")).to_have_count(3, timeout=15000)


@pytest.mark.usefixtures("setup_cir")
def test_display_content_after_republish_complete(page: Page):
    """
    Verify that clicking the back button after a successful republish process returns the user to the create session
    page.
    """
    page.goto("http://localhost:5100/")

    create_session_button = page.get_by_test_id("create-session-btn")

    create_session_button.click()

    republish_button = page.get_by_test_id("republish-btn")
    republish_button.click()

    page.wait_for_timeout(15000)

    page.go_back()

    create_session_button.click()

    expect(republish_button).to_be_enabled()
    expect(page.get_by_text("Not started")).to_have_count(3)


@pytest.mark.usefixtures("setup_cir")
def test_display_content_after_republish_complete_after_closing_page(page: Page):
    """
    Verify that clicking the back button after a successful republish process returns the user to the create session
    page.
    """
    page.goto("http://localhost:5100/")

    create_session_button = page.get_by_test_id("create-session-btn")

    create_session_button.click()

    republish_button = page.get_by_test_id("republish-btn")
    republish_button.click()

    page.wait_for_timeout(15000)

    new_page = page.context.new_page()

    page.close()

    new_page.goto("http://localhost:5100/")

    expect(new_page).to_have_title(re.compile(r"Collection Instrument Migration Service \(CIMS\)"))

    second_create_session_button = new_page.get_by_test_id("create-session-btn")

    second_create_session_button.click()

    second_republish_button = new_page.get_by_test_id("republish-btn")

    expect(second_republish_button).to_be_enabled()
    expect(new_page.get_by_text("Not started")).to_have_count(3)


@pytest.mark.usefixtures("setup_cir")
def test_display_content_republish_in_progress_after_navigating_back(page: Page):
    """Verify that clicking the create session button displays the expected content after making a request to CIR."""
    page.goto("http://localhost:5100/")

    create_session_button = page.get_by_test_id("create-session-btn")

    create_session_button.click()

    republish_button = page.get_by_test_id("republish-btn")

    republish_button.click()

    page.wait_for_timeout(1000)

    page.go_back()

    create_session_button.click()

    expect(republish_button).to_be_disabled()

    expect(page.get_by_text("Success")).to_have_count(3, timeout=15000)


@pytest.mark.usefixtures("setup_cir")
def test_display_content_republish_in_progress_after_closing_page(page: Page):
    """Verify that clicking the create session button displays the expected content after making a request to CIR."""
    page.goto("http://localhost:5100/")

    create_session_button = page.get_by_test_id("create-session-btn")

    create_session_button.click()

    republish_button = page.get_by_test_id("republish-btn")

    republish_button.click()

    page.close()

    new_page = page.context.new_page()

    new_page.goto("http://localhost:5100/")

    second_republish_button = new_page.get_by_test_id("republish-btn")

    expect(second_republish_button).to_be_disabled()

    new_page.wait_for_timeout(20000)
