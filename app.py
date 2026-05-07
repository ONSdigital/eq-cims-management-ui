"""
Flask application factory for the EQ CIR Management UI. Configures logging, Jinja, the Design System, etc.
It also creates the Flask application and registers the blueprints.

Functions:
    create_app
    env_override
    jinja_config
    design_system_config
    configure_secure_headers
    configure_logging
"""

import json
import logging
import os
import sys
from pathlib import Path

import structlog
from dotenv import load_dotenv
from flask import Flask
from flask_talisman import Talisman
from jinja2 import ChainableUndefined, FileSystemLoader
from semver.version import Version

from eq_cims_management_ui.config.config import DefaultConfig
from eq_cims_management_ui.errors.routes import errors_blueprint
from eq_cims_management_ui.main.routes import main_blueprint, view_session_blueprint
from eq_cims_management_ui.utils.routes import utils_blueprint

# Load .env file
load_dotenv()

talisman = Talisman()

logger = structlog.get_logger()


def create_app(app_config: type[DefaultConfig]) -> Flask:
    """
    Flask application factory, used to isolate the instance of the Flask application.
    See https://flask.palletsprojects.com/en/2.2.x/patterns/appfactories/ .
    """
    application = Flask(__name__)

    application.config.from_object(app_config)
    application.static_folder = Path("static")

    application.register_blueprint(main_blueprint)
    application.register_blueprint(errors_blueprint)
    application.register_blueprint(view_session_blueprint)
    application.register_blueprint(utils_blueprint)

    jinja_config(application)
    design_system_config()
    configure_secure_headers(application)

    return application


def env_override(value: str, key: str) -> str:
    """
    Jinja filter to override a value with an environment variable if it exists.
    :param value: The default value to use if the environment variable is not set.
    :param key: The name of the environment variable to check.
    :return: The value of the environment variable if it exists, otherwise the default value.
    """
    return os.getenv(key, value)


def jinja_config(application: Flask) -> None:
    """
    Configuration for the Flask Jinja2 component. Here we provide a custom loader,
    so we can load from an array of sources.

    :param application: The Flask application.
    """
    # loader for local templates and design system component templates
    file_system_loader = FileSystemLoader([Path("./node_modules/@ons/design-system"), Path("./templates")])

    application.jinja_loader = file_system_loader
    application.jinja_env.undefined = ChainableUndefined
    application.jinja_env.filters["env_override"] = env_override

    # Clean up white space.
    application.jinja_env.trim_blocks = True
    application.jinja_env.lstrip_blocks = True


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


def configure_secure_headers(application: Flask) -> None:
    """
    Use Flask-Talisman to configure secure headers for the application.

    :param application: The Flask application.
    """
    csp = {
        "default-src": ["'self'", application.config["CDN_URL"]],
        "font-src": ["'self'", application.config["CDN_URL"]],
        "script-src": [
            "'self'",
            application.config["CDN_URL"],
            "https://*.googletagmanager.com",
            "https://*.google-analytics.com",
        ],
        "style-src": ["'self'", application.config["CDN_URL"]],
        "connect-src": [
            "'self'",
            "https://*.googletagmanager.com",
            "https://*.google-analytics.com",
        ],
        "frame-src": [],
        "img-src": ["'self'", "data:", application.config["CDN_URL"]],
        "object-src": ["'none'"],
        "base-uri": ["'none'"],
        "manifest-src": ["'self'", application.config["CDN_URL"]],
    }
    talisman.init_app(
        application,
        force_https=False,  # HTTPS is managed by infrastructure
        content_security_policy=csp,
        content_security_policy_nonce_in=["script-src"],
        frame_options="DENY",
        strict_transport_security=True,
        strict_transport_security_max_age=31536000,
        session_cookie_secure=application.config["SESSION_COOKIE_SECURE"],
    )


def configure_logging():
    """
    Configures logging for the application using structlog. The log level is set based on the LOG_LEVEL environment
    variable, with DEBUG level if LOG_LEVEL is set to "DEBUG" and "INFO" level otherwise. Logs are output to stdout,
    while error logs are output to stderr. The log format is set to a human-readable console format in "DEBUG" mode and
    JSON format in other modes.
    """
    log_level = logging.DEBUG if os.getenv("LOG_LEVEL") == "DEBUG" else logging.INFO

    error_log_handler = logging.StreamHandler(sys.stderr)
    error_log_handler.setLevel(logging.ERROR)

    renderer_processor = (
        structlog.dev.ConsoleRenderer() if log_level == logging.DEBUG else structlog.processors.JSONRenderer()
    )

    logging.basicConfig(level=log_level, format="%(message)s", stream=sys.stdout)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            renderer_processor,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
    )


configure_logging()
app = create_app(DefaultConfig)

if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 5100))
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host=host, port=port, debug=debug_mode)
