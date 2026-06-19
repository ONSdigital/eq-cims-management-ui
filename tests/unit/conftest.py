# pylint: disable=redefined-outer-name

"""
Fixtures for testing the EQ CIR Management UI application.
These fixtures provide a test client and an application instance for unit tests.
"""

from unittest import mock
from unittest.mock import MagicMock

import pytest
import requests
from google.api_core.exceptions import RetryError

from app import create_app
from eq_cims_management_ui.config.config import DefaultConfig

test_metadata = [
    {
        "ci_version": 1,
        "data_version": "0.0.1",
        "validator_version": "0.0.1",
        "classifier_type": "form_type",
        "classifier_value": "1234",
        "guid": "xyz",
        "language": "en",
        "published_at": "2026-05-21T13:57:24.276672Z",
        "survey_id": "999",
        "title": "Test Survey",
        "status": "Not started",
    },
    {
        "ci_version": 1,
        "data_version": "0.0.1",
        "validator_version": "0.0.1",
        "classifier_type": "form_type",
        "classifier_value": "1234",
        "guid": "abc",
        "language": "en",
        "published_at": "2026-05-21T13:56:55.905000Z",
        "survey_id": "999",
        "title": "Test Survey 2",
        "status": "Not started",
    },
]


def setup_mock_firestore():
    """
    Set up a mock Firestore client and document reference for testing.

    Returns:
        mock_session_doc_ref (MagicMock): A mock instance of a Firestore document reference.
        mock_flask_current_app (MagicMock): A mock instance of the current Flask app with the global variable for
        Firestore set.
    """
    mock_flask_current_app = MagicMock()
    mock_firestore_handler = MagicMock()
    mock_session_doc_ref = MagicMock()

    mock_flask_current_app.config = {"firestore_handler": mock_firestore_handler}

    mock_firestore_handler.retrieve_latest_session.return_value = mock_session_doc_ref

    return mock_session_doc_ref, mock_flask_current_app


def mock_setup_app_with_firestore_handler():
    """Create a mocked Flask global with a mocked firestore_handler in config."""
    mock_flask_current_app = MagicMock()
    mock_firestore_handler = MagicMock()
    mock_flask_current_app.config = {"firestore_handler": mock_firestore_handler}
    return mock_flask_current_app, mock_firestore_handler


def setup_firestore_query_mock():
    """Set up a mock Firestore client and query list for testing."""
    mock_client = MagicMock()
    mock_collection = MagicMock()
    mock_query_list = MagicMock()

    mock_client.collection.return_value = mock_collection

    mock_collection.order_by.return_value = mock_query_list
    mock_query_list.limit.return_value = mock_query_list

    return mock_client, mock_query_list


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
        to_dict=lambda: {"status": "Not started", "created_at": "2026-05-05T15:00:43.198172+01:00"},
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
def mock_firestore_ci_metadata_stream(monkeypatch):
    """Mock the Firestore client to simulate streaming collection instrument metadata."""
    mock_flask_current_app, mock_firestore_handler = mock_setup_app_with_firestore_handler()
    mock_session_ref = MagicMock()
    mock_collection = MagicMock()

    mock_ci_metadata = [MagicMock(to_dict=lambda d=ci_metadata: d) for ci_metadata in test_metadata]

    mock_firestore_handler.latest_session_document_ref = mock_session_ref

    mock_session_ref.collection.return_value = mock_collection
    mock_collection.stream.return_value = mock_ci_metadata

    monkeypatch.setattr("eq_cims_management_ui.utils.database.application_logic.current_app", mock_flask_current_app)


@pytest.fixture
def mock_invalid_firestore_metadata_stream(monkeypatch):
    """Mock the Firestore client to simulate a RetryError when failing to stream collection instrument metadata."""
    mock_flask_current_app, mock_firestore_handler = mock_setup_app_with_firestore_handler()
    mock_session_ref = MagicMock()
    mock_collection = MagicMock()

    mock_firestore_handler.latest_session_document_ref = mock_session_ref
    mock_session_ref.collection.return_value = mock_collection
    mock_collection.stream.side_effect = RetryError(
        cause=Exception("RetryError"),
        message="Mock RetryError Exception raise",
    )

    monkeypatch.setattr("eq_cims_management_ui.utils.database.application_logic.current_app", mock_flask_current_app)


@pytest.fixture
def mock_retrieve_latest_session(monkeypatch):
    """Mock getting the latest session document reference from Firestore, simulating a session being present."""
    mock_client, mock_query_list = setup_firestore_query_mock()
    mock_document_snapshot = MagicMock()
    mock_session_ref = "abc-def-ghi"

    mock_query_list.get.return_value = [mock_document_snapshot]

    mock_document_snapshot.reference = mock_session_ref

    monkeypatch.setattr("eq_cims_management_ui.utils.database.firestore_handler.Client", lambda: mock_client)


@pytest.fixture
def mock_retrieve_latest_session_not_present(monkeypatch):
    """Mock no session document reference being returned from Firestore, simulating no session being present."""
    mock_client, mock_query_list = setup_firestore_query_mock()
    mock_query_list.get.return_value = []

    monkeypatch.setattr("eq_cims_management_ui.utils.database.firestore_handler.Client", lambda: mock_client)


@pytest.fixture
def mock_retrieve_latest_session_failure(monkeypatch):
    """Mock a failure when attempting to retrieve the latest session from Firestore."""
    mock_client, mock_query_list = setup_firestore_query_mock()
    mock_query_list.get.side_effect = RetryError(
        cause=Exception("RetryError"),
        message="Mock RetryError Exception raise",
    )

    monkeypatch.setattr("eq_cims_management_ui.utils.database.firestore_handler.Client", lambda: mock_client)


@pytest.fixture
def mock_create_database_session(monkeypatch):
    """Fixture to mock the create_database_session method."""
    mock_current_app = MagicMock()
    mock_firestore_handler = MagicMock()

    mock_current_app.config = {"firestore_handler": mock_firestore_handler}

    monkeypatch.setattr("eq_cims_management_ui.utils.database.application_logic.current_app", mock_current_app)

    with mock.patch.object(
        mock_current_app.config["firestore_handler"],
        "create_database_session",
    ) as mock_create_database_session_test:
        yield mock_create_database_session_test


@pytest.fixture
def mock_firestore_get_session(monkeypatch):
    """Mock getting latest session doc reference from Firestore, simulating a session with 'Not started' status."""
    mock_session_doc_ref, mock_flask_current_app = setup_mock_firestore()

    mock_session_doc_ref.get.return_value = MagicMock(
        to_dict=lambda: {"status": "Not started", "created_at": "2026-05-05T15:00:43.198172+01:00"},
    )

    monkeypatch.setattr("eq_cims_management_ui.utils.database.application_logic.current_app", mock_flask_current_app)


@pytest.fixture
def mock_firestore_get_session_in_progress(monkeypatch):
    """Mock getting latest session doc reference from Firestore, simulating a session with 'Running' status."""
    mock_session_doc_ref, mock_flask_current_app = setup_mock_firestore()

    mock_session_doc_ref.get.return_value = MagicMock(
        to_dict=lambda: {"status": "Running", "created_at": "2026-05-05T15:00:43.198172+01:00"},
    )

    monkeypatch.setattr("eq_cims_management_ui.utils.database.application_logic.current_app", mock_flask_current_app)


@pytest.fixture
def mock_firestore_get_session_no_session(monkeypatch):
    """Mock getting latest session doc reference from Firestore, simulating no session being present."""
    mock_flask_current_app = MagicMock()
    mock_firestore_handler = MagicMock()

    mock_flask_current_app.firestore_handler = mock_firestore_handler

    mock_firestore_handler.retrieve_latest_session.return_value = None

    monkeypatch.setattr("eq_cims_management_ui.utils.database.application_logic.current_app", mock_flask_current_app)


@pytest.fixture
def mock_document_reference():
    """
    Fixture to mock a Firestore document reference.

    Returns:
        MagicMock: A mock instance of a Firestore document reference with an id attribute.
    """
    mock_doc_ref = MagicMock()
    mock_doc_ref.id = "abc-def-ghi"

    return mock_doc_ref


# pylint: disable=too-few-public-methods
class MockCirResponse:
    """Class to mock the response from the CIR API."""

    def __init__(self, response):
        self.response = response

    def json(self) -> dict:
        """Return the mocked response as a JSON object."""
        return self.response


# pylint: disable=too-few-public-methods
class MockStatus:
    """Class to mock the status code received from the CIR API."""

    def __init__(self, status_code):
        self.status_code = status_code


@pytest.fixture()
def mock_valid_cir_requests(monkeypatch):
    """
    Fixture to mock the requests library and return a predefined response for CIR metadata requests. This represents the
    scenario where the CIR API is available and returns valid metadata for collection instruments.

    Args:
        monkeypatch: The pytest fixture used to patch the requests library.
    """

    def mock_status(*_args, **_kwargs):
        return MockStatus(200)

    def mock_cir_metadata(*_args, **_kwargs):
        return MockCirResponse(test_metadata)

    responses = iter([mock_status(), mock_cir_metadata()])

    def mock_get(*_args, **_kwargs):
        return next(responses)

    monkeypatch.setattr(requests, "get", mock_get)


@pytest.fixture()
def mock_invalid_cir_metadata_requests(monkeypatch):
    """
    Fixture to mock the requests library and return a predefined response for CIR metadata requests where the CIR API
    is available but returns an empty response as CI metadata cannot be retrieved.

    Args:
        monkeypatch: The pytest fixture used to patch the requests library.
    """

    def mock_status(*_args, **_kwargs):
        return MockStatus(200)

    def mock_cir_metadata_empty(*_args, **_kwargs):
        return MockCirResponse({"status": "error", "message": "No CI found"})

    responses = iter([mock_status(), mock_cir_metadata_empty()])

    def mock_get(*_args, **_kwargs):
        return next(responses)

    monkeypatch.setattr(requests, "get", mock_get)


@pytest.fixture()
def mock_erroneous_cir_status(monkeypatch):
    """
    Fixture to mock the requests library and return a predefined response for CIR status requests where the CIR API is
    not available.

    Args:
        monkeypatch: The pytest fixture used to patch the requests library.
    """

    def mock_status(*_args, **_kwargs):
        raise requests.exceptions.ConnectionError

    monkeypatch.setattr(requests, "get", mock_status)
