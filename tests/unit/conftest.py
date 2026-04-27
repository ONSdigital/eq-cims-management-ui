# pylint: disable=redefined-outer-name

"""
Fixtures for testing the EQ CIR Management UI application.
These fixtures provide a test client and an application instance for unit tests.
"""

from unittest import mock
from unittest.mock import MagicMock

import pytest
from google.api_core.exceptions import RetryError

from eq_cims_management_ui import create_app
from eq_cims_management_ui.config.config import DefaultConfig


@pytest.fixture
def app():
    """
    Fixture to create and configure a Flask application instance for testing.
    This fixture initializes the application with the default configuration,
    sets it to testing mode, and yields the application instance for use in tests.

    Returns:
        Flask: The configured Flask application instance.
    """
    app = create_app(DefaultConfig)
    app.testing = True
    yield app


@pytest.fixture
def client(app):
    """
    Fixture to create a test client for the Flask application.
    This fixture uses the application instance created by the `app` fixture
    to create a test client that can be used to simulate HTTP requests during tests.

    Args:
        app (Flask): The Flask application instance.

    Returns:
        FlaskClient: A test client instance for the application.
    """
    return app.test_client()


@pytest.fixture
def mock_firestore_session(monkeypatch):
    """
    Fixture to mock the Firestore client and all interactions with the database
    for testing purposes. Sets the value returned by the get method of the document
    reference to a predefined output of session data.

    Args:
        monkeypatch: The pytest fixture used to patch the firestore client.
    """
    mock_client = MagicMock()
    mock_collection = MagicMock()
    mock_document = MagicMock()

    mock_client.collection.return_value = mock_collection
    mock_collection.document.return_value = mock_document

    mock_document.get.return_value = MagicMock(
        to_dict=lambda: {"status": "Not started", "created_at": "2026-04-02 12:17:04.1775128624"},
    )

    monkeypatch.setattr("eq_cims_management_ui.utils.database.firestore_handler.Client", lambda: mock_client)


@pytest.fixture
def mock_erroneous_firestore_session(monkeypatch):
    """
    Fixture to mock an erroneous/missing Firestore client and all interactions with
    the database for testing purposes. Mocks the set method of the document reference to
    raise a RetryError when called. This simulates an error when trying to create a session with
    an erroneous database instance.

    Args:
        monkeypatch: The pytest fixture used to patch the firestore client.
    """
    mock_client = MagicMock()
    mock_collection = MagicMock()
    mock_document = MagicMock()

    mock_client.collection.return_value = mock_collection
    mock_collection.document.return_value = mock_document

    mock_document.set.side_effect = RetryError(cause=Exception("RetryError"), message="Mock RetryError Exception raise")

    monkeypatch.setattr("eq_cims_management_ui.utils.database.firestore_handler.Client", lambda: mock_client)


@pytest.fixture
def mock_client():
    """
    Fixture to mock the Firestore Client class.

    Yields:
        - mock_client: A mock instance of the Firestore Client class.
    """
    with mock.patch("eq_cims_management_ui.utils.database.firestore_handler.Client") as mock_client:
        yield mock_client


@pytest.fixture
def mock_create_database_session():
    """Fixture to mock the create_database_session method."""
    with mock.patch(
        "eq_cims_management_ui.utils.database.firestore_logic.FirestoreHandler.create_database_session",
    ) as mock_create_database_session:
        yield mock_create_database_session
