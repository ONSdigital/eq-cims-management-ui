"""
Unit tests for the application factory and configuration.
This module contains tests for the application factory, Jinja configuration,
design system configuration, and secure headers.
"""

import json
import os

from eq_cims_management_ui import create_app, design_system_config, env_override
from eq_cims_management_ui.config.config import DefaultConfig


class TestConfig(DefaultConfig):  # pylint: disable=too-few-public-methods
    """Test configuration for the Flask application."""

    CDN_URL = "https://cdn.example.com"
    SESSION_COOKIE_SECURE = False


def test_app_creation_registers_blueprints(app):
    """Test that the application factory registers the blueprints correctly."""
    rules = [rule.endpoint for rule in app.url_map.iter_rules()]

    assert "main.index" in rules
    assert "main.status" in rules
    assert "utils.trigger_400" in rules
    assert "utils.trigger_401" in rules
    assert "utils.trigger_403" in rules
    assert "utils.trigger_405" in rules
    assert "utils.trigger_500" in rules


def test_jinja_config_adds_env_override_filter(app):
    """Test that the Jinja environment is configured correctly."""
    assert "env_override" in app.jinja_env.filters
    assert app.jinja_env.trim_blocks is True
    assert app.jinja_env.lstrip_blocks is True


def test_env_override_returns_env_value(monkeypatch):
    """Test that the env_override function returns the environment variable value."""
    monkeypatch.setenv("MY_KEY", "from_env")

    assert env_override("default", "MY_KEY") == "from_env"


def test_env_override_returns_default_when_env_not_set():
    """Test that the env_override function returns the default value when the environment variable is not set."""
    assert env_override("default", "UNSET_KEY") == "default"


def test_design_system_config_sets_env(monkeypatch, tmp_path):
    """Test that the design system configuration sets the environment variable correctly."""
    package_json = tmp_path / "package.json"
    package_json.write_text(json.dumps({"dependencies": {"@ons/design-system": "1.2.3"}}))

    monkeypatch.chdir(tmp_path)

    design_system_config()
    assert os.environ["DESIGN_SYSTEM_VERSION"] == "1.2.3"


def test_design_system_config_logs_invalid_version(monkeypatch, tmp_path, caplog):
    """Test that the design system configuration logs an error for an invalid version."""
    package_json = tmp_path / "package.json"
    package_json.write_text(json.dumps({"dependencies": {"@ons/design-system": "invalid_version"}}))

    monkeypatch.chdir(tmp_path)

    with caplog.at_level("ERROR"):
        design_system_config()

    assert "semantic versioning" in caplog.text


def test_design_system_config_logs_missing_dependency(monkeypatch, tmp_path, caplog):
    """Test that the design system configuration logs an error when the dependency is missing."""
    package_json = tmp_path / "package.json"
    package_json.write_text(json.dumps({"dependencies": {"some-other-lib": "1.0.0"}}))

    monkeypatch.chdir(tmp_path)

    with caplog.at_level("ERROR"):
        design_system_config()

    assert "@ons/design-system' dependency is not found" in caplog.text


def test_secure_headers_configured():
    """Test that the secure headers are configured correctly."""
    app = create_app(TestConfig)

    @app.route("/test")
    def test_route():
        return "Hello"

    client = app.test_client()
    response = client.get("/test")

    # Check that Talisman has added the CSP header
    csp_header = response.headers.get("Content-Security-Policy")
    assert csp_header is not None
    assert "default-src" in csp_header
