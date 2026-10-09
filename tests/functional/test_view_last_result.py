# pylint: disable=missing-module-docstring

import json
import re

import pytest
import requests
from playwright.sync_api import Page, expect


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


@pytest.mark.usefixtures("setup_cir")
def test_view_last_session_after_completed_session(page: Page):
    """
    Verify that after a completed session, clicking the "View last session" button displays the results of the last
    completed session.
    """
    page.goto("http://localhost:5100/")

    expect(page).to_have_title(re.compile(r"Collection Instrument Migration Service \(CIMS\)"))

    create_session_button = page.get_by_test_id("create-session-btn")

    create_session_button.click()

    expect(page.get_by_role("heading", name=re.compile(r"Collection instruments"))).to_be_visible()

    expect(page.get_by_text("75f9d538-dda2-4852-ab6d-729391da2cdc")).to_be_visible()
    expect(page.get_by_text("35ef7238-d689-4285-adee-bd662a051f83")).to_be_visible()
    expect(page.get_by_text("cccac6bb-82de-4eca-9cee-6ca59b2751db")).to_be_visible()

    republish_button = page.get_by_test_id("republish-btn")
    home_button = page.get_by_test_id("home-btn")

    expect(page.get_by_text("Not started")).to_have_count(3)

    republish_button.click()
    expect(republish_button).to_be_disabled()

    expect(page.get_by_text("Success")).to_have_count(3, timeout=15000)

    expect(republish_button).to_be_disabled()
    expect(home_button).to_be_enabled()

    home_button.click()

    view_last_session_button = page.get_by_test_id("last-session-btn")

    expect(view_last_session_button).to_be_enabled()

    view_last_session_button.click()

    expect(page.get_by_role("heading", name=re.compile(r"Collection instruments"))).to_be_visible()

    expect(republish_button).not_to_be_in_viewport()

    expect(page.get_by_text("75f9d538-dda2-4852-ab6d-729391da2cdc")).to_be_visible()
    expect(page.get_by_text("35ef7238-d689-4285-adee-bd662a051f83")).to_be_visible()
    expect(page.get_by_text("cccac6bb-82de-4eca-9cee-6ca59b2751db")).to_be_visible()

    expect(page.get_by_text("Success")).to_have_count(3)


@pytest.mark.usefixtures("setup_cir")
def test_view_last_session_shows_completed_session(page: Page):
    """
    Verify that after creating a session and not completing it, only the previous completed session is displayed when
    clicking the "View last session" button.
    """
    page.goto("http://localhost:5100/")

    expect(page).to_have_title(re.compile(r"Collection Instrument Migration Service \(CIMS\)"))

    create_session_button = page.get_by_test_id("create-session-btn")

    create_session_button.click()

    home_button = page.get_by_test_id("home-btn")

    expect(page.get_by_text("Not started")).to_have_count(3)

    expect(home_button).to_be_enabled()

    home_button.click()

    view_last_session_button = page.get_by_test_id("last-session-btn")

    expect(view_last_session_button).to_be_enabled()

    view_last_session_button.click()

    expect(page.get_by_text("75f9d538-dda2-4852-ab6d-729391da2cdc")).to_be_visible()
    expect(page.get_by_text("35ef7238-d689-4285-adee-bd662a051f83")).to_be_visible()
    expect(page.get_by_text("cccac6bb-82de-4eca-9cee-6ca59b2751db")).to_be_visible()

    expect(page.get_by_text("Success")).to_have_count(3)
    expect(page.get_by_text("Not started")).to_have_count(0)
