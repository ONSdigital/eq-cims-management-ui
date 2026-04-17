"""Flask application factory for the EQ CIR Management UI."""

import json
import logging
import os
from pathlib import Path

from flask import Flask
from flask_talisman import Talisman
from jinja2 import ChainableUndefined, FileSystemLoader
from semver.version import Version

from eq_cims_management_ui.config.config import DefaultConfig
from eq_cims_management_ui.errors.routes import errors_blueprint
from eq_cims_management_ui.main.routes import main_blueprint, view_session_blueprint
from eq_cims_management_ui.utils.routes import utils_blueprint

logger = logging.getLogger()

talisman = Talisman()


def create_app(app_config: type[DefaultConfig]) -> Flask:
    """
    Flask application factory, used to isolate the instance of the Flask application.
    See https://flask.palletsprojects.com/en/2.2.x/patterns/appfactories/ .
    """
    app = Flask(__name__)

    app.config.from_object(app_config)
    app.static_folder = Path("../static")

    app.register_blueprint(main_blueprint)
    app.register_blueprint(errors_blueprint)
    app.register_blueprint(view_session_blueprint)
    app.register_blueprint(utils_blueprint)

    jinja_config(app)
    design_system_config()
    configure_secure_headers(app)

    return app


def env_override(value: str, key: str) -> str:
    """
    Jinja filter to override a value with an environment variable if it exists.
    :param value: The default value to use if the environment variable is not set.
    :param key: The name of the environment variable to check.
    :return: The value of the environment variable if it exists, otherwise the default value.
    """
    return os.getenv(key, value)


def jinja_config(app: Flask) -> None:
    """
    Configuration for the Flask Jinja2 component. Here we provide a custom loader,
    so we can load from an array of sources.

    :param app: The Flask application.
    """
    # loader for local templates and design system component templates
    file_system_loader = FileSystemLoader([Path("./node_modules/@ons/design-system"), Path("./templates")])

    app.jinja_loader = file_system_loader
    app.jinja_env.undefined = ChainableUndefined
    app.jinja_env.filters["env_override"] = env_override

    # Clean up white space.
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True


def design_system_config() -> None:
    """
    Set the version of the design system to an environment variable and add an
    environment variable filter so environment variables can be read from within
    Jinja. This enables the design system version to be defined once within the
    package.json file and then reused throughout the application. Primarily to
    declare the CSS version to use.
    """
    with open(Path("./package.json"), encoding="utf-8") as file:
        package_json = json.load(file)

        design_system_version = package_json.get("dependencies", {}).get("@ons/design-system")

        if not design_system_version:
            logger.exception(
                "The '@ons/design-system' dependency is not found in package.json. "
                "Please ensure it is listed under 'dependencies'.",
            )
        elif not Version.is_valid(design_system_version):
            logger.exception(
                "The '@ons/design-system' dependency version is invalid. Please ensure it follows semantic versioning.",
            )
        else:
            os.environ["DESIGN_SYSTEM_VERSION"] = design_system_version


def configure_secure_headers(app: Flask) -> None:
    """
    Use Flask-Talisman to configure secure headers for the application.

    :param app: The Flask application.
    """
    csp = {
        "default-src": ["'self'", app.config["CDN_URL"]],
        "font-src": ["'self'", app.config["CDN_URL"]],
        "script-src": [
            "'self'",
            app.config["CDN_URL"],
            "https://*.googletagmanager.com",
            "https://*.google-analytics.com",
        ],
        "style-src": ["'self'", app.config["CDN_URL"]],
        "connect-src": [
            "'self'",
            "https://*.googletagmanager.com",
            "https://*.google-analytics.com",
        ],
        "frame-src": [],
        "img-src": ["'self'", "data:", app.config["CDN_URL"]],
        "object-src": ["'none'"],
        "base-uri": ["'none'"],
        "manifest-src": ["'self'", app.config["CDN_URL"]],
    }
    talisman.init_app(
        app,
        force_https=False,  # HTTPS is managed by infrastructure
        content_security_policy=csp,
        content_security_policy_nonce_in=["script-src"],
        frame_options="DENY",
        strict_transport_security=True,
        strict_transport_security_max_age=31536000,
        session_cookie_secure=app.config["SESSION_COOKIE_SECURE"],
    )
