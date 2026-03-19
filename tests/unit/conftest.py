# pylint: disable=redefined-outer-name

"""Fixtures for testing the EQ CIR Management UI application.
These fixtures provide a test client and an application instance for unit tests.
"""

import pytest

from eq_cims_management_ui import create_app
from eq_cims_management_ui.config.config import DefaultConfig


@pytest.fixture
def app():
    """Fixture to create and configure a Flask application instance for testing.
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
    """Fixture to create a test client for the Flask application.
    This fixture uses the application instance created by the `app` fixture
    to create a test client that can be used to simulate HTTP requests during tests.

    Args:
        app (Flask): The Flask application instance.

    Returns:
        FlaskClient: A test client instance for the application.
    """
    return app.test_client()
