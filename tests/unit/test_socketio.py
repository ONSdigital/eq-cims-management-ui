import unittest
from unittest.mock import patch

import flask

from app import create_app
from eq_cims_management_ui.config.config import DefaultConfig
from eq_cims_management_ui.main.routes import emit_status
from eq_cims_management_ui.utils.socketio import socketio


class TestSocketIO(unittest.TestCase):
    def test_connect(self):
        app = create_app(DefaultConfig)
        client = socketio.test_client(app, auth={"foo": "bar"})

        self.assertTrue(client.is_connected())

        self.assertTrue("republish" in client.socketio.server.handlers["/"])
        self.assertTrue("connect" in client.socketio.server.handlers["/"])

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
        with app.app_context():
            flask.current_app.extensions["socketio"] = socketio
            with patch("eq_cims_management_ui.main.routes.update_ci_status") as mock_update_ci_status:
                with app.test_request_context():
                    flask.request.namespace = "/"
                    emit_status("f3bb3302-04a1-4bea-9c32-9c46a9a93306", "Not Started", "test-session-123")
                    mock_update_ci_status.assert_called()
