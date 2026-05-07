"""Module testing error responses."""

import pytest

from app import create_app
from eq_cims_management_ui.config import config


@pytest.fixture(name="test_client")
def create_client():
    """Creates and configures a test client for the application."""
    app = create_app(config.DefaultConfig)
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


@pytest.mark.parametrize(
    "route, expected_status, expected_text",
    [
        ("/page-not-found", 404, "Page not found"),
        ("/405", 405, "Page not found"),  # 405 returns the 404 page
        ("/500", 500, "Sorry, there is a problem with the service"),
        ("/400", 400, "Sorry, there is a problem with the service"),  # 400 returns 500 content
        ("/403", 403, "Forbidden"),
        ("/401", 401, "Unauthorised"),
    ],
)
def test_error_responses(test_client, route, expected_status, expected_text):
    """Test various error routes of the application."""
    response = test_client.get(route)
    assert response.status_code == expected_status
    assert expected_text in response.get_data(as_text=True)
