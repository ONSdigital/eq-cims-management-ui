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
    mock_current_app = MagicMock()
    mock_firestore_handler = MagicMock()
    mock_session_ref = MagicMock()
    mock_collection = MagicMock()

    mock_ci_metadata = [
        MagicMock(to_dict=lambda d=ci_metadata: d) for ci_metadata in [
            {"ci_version": 1, "data_version": "0.0.1", "validator_version": "0.0.1", "classifier_type": "form_type",
             "classifier_value": "1234", "guid": "xyz", "language": "en", "published_at": "2026-05-21T13:57:24.276672Z",
             "survey_id": "999", "title": "Test Survey", "status": "Not started"},
            {"ci_version": 1, "data_version": "0.0.1", "validator_version": "0.0.1", "classifier_type": "form_type",
             "classifier_value": "1234", "guid": "abc", "language": "en", "published_at": "2026-05-21T13:56:55.905000Z",
             "survey_id": "999", "title": "Test Survey 2", "status": "Not started"},
        ]
    ]

    mock_firestore_handler.latest_session_document_ref = mock_session_ref
    mock_current_app.config = {"firestore_handler": mock_firestore_handler}

    mock_session_ref.collection.return_value = mock_collection
    mock_collection.stream.return_value = mock_ci_metadata

    monkeypatch.setattr("eq_cims_management_ui.utils.database.firestore_logic.current_app", mock_current_app)


@pytest.fixture
def mock_invalid_firestore_metadata_stream(monkeypatch):
    mock_current_app = MagicMock()
    mock_firestore_handler = MagicMock()
    mock_session_ref = MagicMock()
    mock_collection = MagicMock()

    mock_current_app.config = {"firestore_handler": mock_firestore_handler}
    mock_firestore_handler.latest_session_document_ref = mock_session_ref
    mock_session_ref.collection.return_value = mock_collection
    mock_collection.stream.side_effect = RetryError(cause=Exception("RetryError"), message="Mock RetryError Exception raise")

    monkeypatch.setattr("eq_cims_management_ui.utils.database.firestore_logic.current_app", mock_current_app)


@pytest.fixture
def mock_retrieve_latest_session(monkeypatch):
    mock_client = MagicMock()
    mock_collection = MagicMock()
    mock_query_list = MagicMock()
    mock_document_snapshot = MagicMock()
    mock_session_ref = "abc-def-ghi"

    mock_client.collection.return_value = mock_collection

    mock_collection.order_by.return_value = mock_query_list
    mock_query_list.limit.return_value = mock_query_list
    mock_query_list.get.return_value = [mock_document_snapshot]

    mock_document_snapshot.reference = mock_session_ref

    monkeypatch.setattr("eq_cims_management_ui.utils.database.firestore_handler.Client", lambda: mock_client)


@pytest.fixture
def mock_retrieve_latest_session_not_present(monkeypatch):
    mock_client = MagicMock()
    mock_collection = MagicMock()
    mock_query_list = MagicMock()

    mock_client.collection.return_value = mock_collection

    mock_collection.order_by.return_value = mock_query_list
    mock_query_list.limit.return_value = mock_query_list
    mock_query_list.get.return_value = []

    monkeypatch.setattr("eq_cims_management_ui.utils.database.firestore_handler.Client", lambda: mock_client)

@pytest.fixture
def mock_retrieve_latest_session_failure(monkeypatch):
    mock_client = MagicMock()
    mock_collection = MagicMock()
    mock_query_list = MagicMock()

    mock_client.collection.return_value = mock_collection

    mock_collection.order_by.return_value = mock_query_list
    mock_query_list.limit.return_value = mock_query_list
    mock_query_list.get.side_effect = RetryError(cause=Exception("RetryError"), message="Mock RetryError Exception raise")

    monkeypatch.setattr("eq_cims_management_ui.utils.database.firestore_handler.Client", lambda: mock_client)


@pytest.fixture
def mock_create_database_session(monkeypatch):
    """Fixture to mock the create_database_session method."""
    mock_current_app = MagicMock()
    mock_firestore_handler = MagicMock()

    mock_current_app.config = {"firestore_handler": mock_firestore_handler}

    monkeypatch.setattr("eq_cims_management_ui.utils.database.firestore_logic.current_app", mock_current_app)

    with mock.patch.object(
        mock_current_app.config["firestore_handler"],
        "create_database_session",
    ) as mock_create_database_session_test:
        yield mock_create_database_session_test


@pytest.fixture
def mock_firestore_get_session(monkeypatch):
    mock_current_app = MagicMock()
    mock_firestore_handler = MagicMock()
    mock_session_doc_ref = MagicMock()

    mock_current_app.config = {"firestore_handler": mock_firestore_handler}

    mock_firestore_handler.retrieve_latest_session.return_value = mock_session_doc_ref

    mock_session_doc_ref.get.return_value = MagicMock(
        to_dict=lambda: {"status": "Not started", "created_at": "2026-05-05T15:00:43.198172+01:00"},
    )

    monkeypatch.setattr("eq_cims_management_ui.utils.database.firestore_logic.current_app", mock_current_app)


@pytest.fixture
def mock_firestore_get_session_in_progress(monkeypatch):
    mock_current_app = MagicMock()
    mock_firestore_handler = MagicMock()
    mock_session_doc_ref = MagicMock()

    mock_current_app.config = {"firestore_handler": mock_firestore_handler}

    mock_firestore_handler.retrieve_latest_session.return_value = mock_session_doc_ref

    mock_session_doc_ref.get.return_value = MagicMock(
        to_dict=lambda: {"status": "Running", "created_at": "2026-05-05T15:00:43.198172+01:00"},
    )

    monkeypatch.setattr("eq_cims_management_ui.utils.database.firestore_logic.current_app", mock_current_app)


@pytest.fixture
def mock_firestore_get_session_no_session(monkeypatch):
    mock_current_app = MagicMock()
    mock_firestore_handler = MagicMock()

    mock_current_app.config = {"firestore_handler": mock_firestore_handler}

    mock_firestore_handler.retrieve_latest_session.return_value = None

    monkeypatch.setattr("eq_cims_management_ui.utils.database.firestore_logic.current_app", mock_current_app)


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


class MockCirResponse:
    def __init__(self, response):
        self.response = response

    def json(self) -> dict:
        return self.response


class MockStatus:
    def __init__(self, status_code):
        self.status_code = status_code


@pytest.fixture()
def mock_valid_cir_requests(monkeypatch):

    def mock_status(*args, **kwargs):
        return MockStatus(200)

    def mock_cir_metadata(*args, **kwargs):
        return MockCirResponse([
            {"ci_version":1, "data_version":"0.0.1", "validator_version":"0.0.1", "classifier_type":"form_type", "classifier_value":"1234", "guid":"xyz", "language":"en", "published_at":"2026-05-21T13:57:24.276672Z", "survey_id":"999", "title":"Test Survey"},
            {"ci_version":1, "data_version":"0.0.1", "validator_version":"0.0.1", "classifier_type":"form_type", "classifier_value":"1234", "guid":"abc", "language":"en", "published_at":"2026-05-21T13:56:55.905000Z", "survey_id":"999", "title":"Test Survey 2"},
        ])

    responses = iter([mock_status(), mock_cir_metadata()])

    def mock_get(*args, **kwargs):
        return next(responses)
    monkeypatch.setattr(requests, "get", mock_get)


@pytest.fixture()
def mock_invalid_cir_metadata_requests(monkeypatch):

    def mock_status(*args, **kwargs):
        return MockStatus(200)

    def mock_cir_metadata_empty(*args, **kwargs):
        return MockCirResponse({"status":"error","message":"No CI found"})

    responses = iter([mock_status(), mock_cir_metadata_empty()])

    def mock_get(*args, **kwargs):
        return next(responses)

    monkeypatch.setattr(requests, "get", mock_get)


@pytest.fixture()
def mock_erroneous_cir_status(monkeypatch):

    def mock_status(*args, **kwargs):
        raise requests.exceptions.ConnectionError

    monkeypatch.setattr(requests, "get", mock_status)
