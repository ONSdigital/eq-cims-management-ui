"""Module testing a basic flask instance."""

import pytest
import requests

from app import create_app
from eq_cims_management_ui.config import config


@pytest.fixture(name="test_client")
def create_client():
    """
    Creates and configures a test client for the application.

    This function initializes the application in testing mode and provides
    a test client that can be used to simulate HTTP requests during unit tests.

    Yields:
        FlaskClient: A test client instance for the application.
    """
    app = create_app(config.DefaultConfig)
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def test_index_route_get_method(test_client):
    """
    Test the index route of the application.

    This test sends a GET request to the root URL ("/") using the test client
    and verifies that the response has a status code of 200 and contains
    the expected content "CI migration process" in the response data.
    """
    response = test_client.get("/")
    assert response.status_code == 200
    assert "CI migration process" in response.get_data(as_text=True)


@pytest.mark.usefixtures("mock_firestore_session", "mock_valid_cir_requests")
def test_create_session_route(test_client):
    """
    Test the create session route.

    This test sends a GET request to the "/create-session" URL using the test client
    and verifies that the response navigates to the "/view-session" endpoint.
    """
    response = test_client.get("/create-session", follow_redirects=True)

    assert response.status_code == 200
    assert response.request.path == "/view-session"


@pytest.mark.usefixtures("mock_erroneous_firestore_session", "mock_valid_cir_requests")
def test_create_session_route_failure_on_firestore(test_client):
    """
    Test the create session route when the database instance isn't present.

    This test sends a GET request to the "/create-session" URL using the test client
    and verifies that a 500 status code is returned alongside an error page.
    """
    response = test_client.get("/create-session", follow_redirects=True)
    assert response.status_code == 500
    assert response.data  # Ensure it's not empty

@pytest.mark.usefixtures("mock_erroneous_cir_status")
def test_create_session_route_failure_on_cir_status(test_client):  # False positive test
    pass
    # with pytest.raises(requests.exceptions.ConnectionError):
    #     response = test_client.get("/create-session", follow_redirects=True)
    #     assert response.status_code == 500
    #     assert response.data  # Ensure it's not empty


@pytest.mark.usefixtures("mock_invalid_cir_metadata_requests")
def test_create_session_route_failure_on_empty_cir_response(test_client):
    pass
    # with pytest.raises(ValueError):
    #     response = test_client.get("/create-session", follow_redirects=True)
    #     assert response.status_code == 500
    #     assert response.data  # Ensure it's not empty


def test_status_check(test_client):
    """
    GIVEN a call to the status check.
    THEN 200 is returned.
    """
    response = test_client.get("/status")

    assert response.status_code == 200


def test_favicon(test_client):
    """
    GIVEN a call to the favicon.
    THEN 200 is returned.
    """
    response = test_client.get("/favicon.ico")
    assert response.status_code == 200
    assert response.mimetype == "image/vnd.microsoft.icon"
    assert response.data  # Make sure it's not empty


@pytest.mark.usefixtures("mock_firestore_session", "mock_firestore_ci_metadata_stream")
def test_view_session(test_client):
    """
    GIVEN a call to the view-session endpoint.
    THEN 200 is returned.
    """
    response = test_client.get("/view-session")

    assert response.status_code == 200
    assert response.data  # Ensure it's not empty
