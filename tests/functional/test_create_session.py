import re # Uses Regex to ensure case sensitivity for tests
from playwright.sync_api import Page, expect

def test_render_initial_page(page: Page):
    page.goto("http://localhost:5100/")

    expect(page).to_have_title(re.compile(r"Collection Instrument Migration Service \(CIMS\)"))
    
def test_confirmation_text_displayed_on_session_creation(page: Page):
    page.goto("http://localhost:5100/")
    
    create_session_button = page.get_by_test_id("create-session-btn")
    create_session_button.click()
    
    expect(page.get_by_text(re.compile(r"Session created"))).to_be_visible()