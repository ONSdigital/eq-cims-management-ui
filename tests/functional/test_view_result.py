# pylint: disable=missing-function-docstring, missing-module-docstring

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
def test_view_ci_result(page: Page):
    page.goto("http://localhost:5100/")

    create_session_button = page.get_by_test_id("create-session-btn")

    create_session_button.click()

    expect(page.get_by_text("Not started")).to_have_count(3)

    republish_button = page.get_by_test_id("republish-btn")

    republish_button.click()

    page.wait_for_timeout(15000)

    ci_status_link = page.get_by_test_id("ci-status-link-75f9d538-dda2-4852-ab6d-729391da2cdc")

    ci_status_link.click()

    expect(page).to_have_url("http://localhost:5100/result/75f9d538-dda2-4852-ab6d-729391da2cdc")
    expect(page.get_by_text("75f9d538-dda2-4852-ab6d-729391da2cdc")).to_be_visible()
    expect(page.get_by_text("Success")).to_be_visible()


@pytest.mark.usefixtures("setup_cir")
def test_view_non_existent_ci_result(page: Page):
    page.goto("http://localhost:5100/")

    create_session_button = page.get_by_test_id("create-session-btn")

    create_session_button.click()
    expect(page.get_by_text("Not started")).to_have_count(3)

    page.goto("http://localhost:5100/result/abc")

    expect(page).to_have_url("http://localhost:5100/result/abc")
    expect(page.get_by_text("Page not found")).to_be_visible()


@pytest.mark.usefixtures("setup_cir")
def test_return_to_view_session_from_results(page: Page):
    page.goto("http://localhost:5100/")

    create_session_button = page.get_by_test_id("create-session-btn")
    create_session_button.click()

    expect(page.get_by_text("Not started")).to_have_count(3)

    republish_button = page.get_by_test_id("republish-btn")
    republish_button.click()

    page.wait_for_timeout(15000)

    ci_status_link = page.get_by_test_id("ci-status-link-35ef7238-d689-4285-adee-bd662a051f83")
    ci_status_link.click()

    expect(page).to_have_url("http://localhost:5100/result/35ef7238-d689-4285-adee-bd662a051f83")

    back_button = page.get_by_test_id("result-back-button")
    back_button.click()

    expect(page).to_have_url("http://localhost:5100/view-session")
    expect(page.get_by_text("Success")).to_have_count(3)


@pytest.mark.usefixtures("setup_cir")
def test_return_to_create_session_from_in_progress_session_is_blocked(page: Page):
    page.goto("http://localhost:5100/")

    create_session_button = page.get_by_test_id("create-session-btn")
    create_session_button.click()

    expect(page.get_by_text("Not started")).to_have_count(3)

    republish_button = page.get_by_test_id("republish-btn")
    republish_button.click()

    page.wait_for_timeout(5000)

    back_button = page.get_by_test_id("view-session-back-button")
    back_button.click()

    expect(page).to_have_url("http://localhost:5100/view-session")

    page.wait_for_timeout(10000)

    back_button.click()

    expect(page).to_have_url("http://localhost:5100/")


@pytest.mark.usefixtures("setup_cir")
def test_return_to_create_session_from_unstarted_session(page):
    page.goto("http://localhost:5100/")

    create_session_button = page.get_by_test_id("create-session-btn")

    create_session_button.click()
    expect(page.get_by_text("Not started")).to_have_count(3)

    back_button = page.get_by_test_id("view-session-back-button")

    back_button.click()

    expect(page).to_have_title(re.compile(r"Collection Instrument Migration Service \(CIMS\)"))
    expect(page.get_by_text("Create session")).to_be_visible()
