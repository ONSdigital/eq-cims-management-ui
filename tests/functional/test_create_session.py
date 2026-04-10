import re  # Uses Regex to ensure case sensitivity for tests

from playwright.sync_api import Page, expect

table_column_headers = [
    "Survey ID",
    "Form type",
    "CIR ID",
    "CIR version",
    "Validator version",
    "Status"
]
    

def test_render_initial_page(page: Page):
    page.goto("http://localhost:5100/")

    expect(page).to_have_title(re.compile(r"Collection Instrument Migration Service \(CIMS\)"))
    
def test_confirmation_text_displayed_on_session_creation(page: Page):
    page.goto("http://localhost:5100/")

    create_session_button = page.get_by_test_id("create-session-btn")
    
    create_session_button.click()
    
    expect(page.get_by_role("heading", name=re.compile(r"Collection instruments"))).to_be_visible()
    expect(page.get_by_test_id("republish-btn")).to_be_visible()
    
    expect(page.get_by_role("table")).to_be_visible()
    
    # Asserts that all column headers are visible in the table
    for header in table_column_headers:
        expect(page.get_by_role("columnheader", name=re.compile(header))).to_be_visible()
