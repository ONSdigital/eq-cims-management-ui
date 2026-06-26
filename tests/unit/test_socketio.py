# pylint: missing-function-docstring

import unittest
from unittest.mock import patch

import flask
import requests

from app import create_app
from eq_cims_management_ui.config.config import DefaultConfig
from eq_cims_management_ui.main.routes import emit_status
from eq_cims_management_ui.utils.socketio import socketio

ci_metadata = [
    {
        "survey_id": "999",
        "form_type": "1234",
        "cir_id": "xyz",
        "cir_version": 1,
        "publish_date": "2026-05-21T13:59:24.276672Z",
        "validator_version": "0.0.1",
        "status": "Not started",
        "error_message": "",
    },
    {
        "survey_id": "999",
        "form_type": "1234",
        "cir_id": "abc",
        "cir_version": 1,
        "publish_date": "2026-05-21T13:59:24.276672Z",
        "validator_version": "0.0.1",
        "status": "Success",
        "error_message": "",
    },
]

republished_ci_metadata = [
    {
        "survey_id": "999",
        "form_type": "1234",
        "cir_id": "xyz",
        "cir_version": 1,
        "publish_date": "2026-05-21T13:59:24.276672Z",
        "validator_version": "0.0.1",
        "status": "Success",
        "error_message": "",
    },
    {
        "survey_id": "999",
        "form_type": "1234",
        "cir_id": "abc",
        "cir_version": 1,
        "publish_date": "2026-05-21T13:59:24.276672Z",
        "validator_version": "0.0.1",
        "status": "Success",
        "error_message": "",
    },
]

failed_republished_ci_metadata = [
    {
        "survey_id": "999",
        "form_type": "1234",
        "cir_id": "xyz",
        "cir_version": 1,
        "publish_date": "2026-05-21T13:59:24.276672Z",
        "validator_version": "0.0.1",
        "status": "Failure",
        "error_message": "",
    },
    {
        "survey_id": "999",
        "form_type": "1234",
        "cir_id": "abc",
        "cir_version": 1,
        "publish_date": "2026-05-21T13:59:24.276672Z",
        "validator_version": "0.0.1",
        "status": "Success",
        "error_message": "",
    },
]


class TestSocketIO(unittest.TestCase):
    def test_connect(self):
        app = create_app(DefaultConfig)
        client = socketio.test_client(app, auth={"foo": "bar"})

        self.assertTrue(client.is_connected())

        self.assertTrue("republish" in client.socketio.server.handlers["/"])  # pyright: ignore
        self.assertTrue("connect" in client.socketio.server.handlers["/"])  # pyright: ignore

        received = client.get_received()
        self.assertEqual(len(received), 0)
        client.disconnect()
        self.assertFalse(client.is_connected())

    def test_connect_with_session_id(self):
        app = create_app(DefaultConfig)
        session_id = "test-session-123"
        with app.app_context():
            flask.current_app.extensions["socketio"] = socketio
            client = socketio.test_client(app, auth={"foo": "bar", "session_id": session_id})

            self.assertTrue(client.is_connected())

        with app.app_context():
            self.assertEqual(app.config["session_id"], session_id)

        client.disconnect()

    def test_emit(self):
        app = create_app(DefaultConfig)
        session_id = "test-session-123"
        with app.app_context():
            flask.current_app.extensions["socketio"] = socketio
            client = socketio.test_client(app, auth={"foo": "bar", "session_id": session_id})
            client.emit(
                "cell_update",
                {"guid": "f3bb3302-04a1-4bea-9c32-9c46a9a93306", "status": "Not Started", "index": 5, "suffix": "info"},
            )
            self.assertTrue(client.is_connected())

        client.disconnect()

    def test_emit_status_function(self):
        app = create_app(DefaultConfig)
        with (
            app.app_context(),
            patch(
                "eq_cims_management_ui.main.routes.update_ci_status",
            ) as mock_update_ci_status,
            app.test_request_context(),
        ):
            flask.current_app.extensions["socketio"] = socketio
            flask.request.namespace = "/"
            emit_status("f3bb3302-04a1-4bea-9c32-9c46a9a93306", "Not Started", "test-session-123")
            mock_update_ci_status.assert_called()

    def test_republish(self):
        app = create_app(DefaultConfig)
        app.config["TEST_AUTHOR_REPUBLISH_API_URL"] = "http://localhost:8081"
        session_id = "test-session-123"

        with app.app_context():
            flask.current_app.extensions["socketio"] = socketio
            client = socketio.test_client(app, auth={"session_id": session_id})

            with (
                patch("eq_cims_management_ui.main.routes.get_collection_instruments") as mock_get_cis,
                patch(
                    "eq_cims_management_ui.main.routes.update_session_status",
                ) as mock_update_session,
                patch(
                    "eq_cims_management_ui.main.routes.update_ci_status",
                ) as mock_update_ci,
                patch(
                    "eq_cims_management_ui.main.routes.requests.get",
                ) as mock_requests_get,
            ):
                mock_get_cis.side_effect = [ci_metadata, republished_ci_metadata]
                mock_requests_get.return_value.json.return_value = {"success": True}

                client.emit("republish")

                mock_update_session.assert_any_call("Running")
                mock_update_session.assert_any_call("Success")
                mock_update_ci.assert_any_call("xyz", "Started")
                mock_update_ci.assert_any_call("abc", "Success")

            client.disconnect()

    def test_republish_failure(self):
        app = create_app(DefaultConfig)
        session_id = "test-session-123"

        with app.app_context():
            flask.current_app.extensions["socketio"] = socketio
            client = socketio.test_client(app, auth={"session_id": session_id})

            with (
                patch("eq_cims_management_ui.main.routes.get_collection_instruments") as mock_get_cis,
                patch(
                    "eq_cims_management_ui.main.routes.update_session_status",
                ) as mock_update_session,
                patch(
                    "eq_cims_management_ui.main.routes.update_ci_status",
                ) as mock_update_ci,
                patch(
                    "eq_cims_management_ui.main.routes.requests.get",
                ) as mock_requests_get,
            ):
                mock_get_cis.side_effect = [ci_metadata, failed_republished_ci_metadata]
                mock_requests_get.side_effect = requests.exceptions.ConnectionError()

                client.emit("republish")

                mock_update_session.assert_any_call("Running")
                mock_update_session.assert_any_call("Failure")
                mock_update_ci.assert_any_call("xyz", "Failure")
                mock_update_ci.assert_any_call("abc", "Success")

            client.disconnect()
