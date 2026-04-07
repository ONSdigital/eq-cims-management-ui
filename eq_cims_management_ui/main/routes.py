"""Routes for the EQ CIR Management UI."""

import logging

from flask import (
    Blueprint,
    render_template,
    request,
)
from google.api_core.exceptions import RetryError

from eq_cims_management_ui.errors.routes import error_content_500
from eq_cims_management_ui.utils.database.firestore_logic import create_session

main_blueprint = Blueprint("main", __name__)

logger = logging.getLogger(__name__)


@main_blueprint.before_request
def before_request_func() -> None:
    """Log the request before it is processed."""
    if request.endpoint != "status":
        message = "Request received"
        logger.info(message)


@main_blueprint.route("/", methods=["GET"])
def index() -> str:
    """UI index.

    :return: 200 index page.
    """
    return render_template("index.html")


@main_blueprint.route("/session", methods=["POST"])
def create_and_view_session() -> str:
    """Creates a new session in the Firestore databases and returns a list of CIs to render on the page.

    Returns:
        str: A rendered HTML page with a message indicating that the session was created. Note: To be updated to
        return a rendered page with a list of CIs.
    """

    session = create_session()
    if session:
        return render_template("index.html", text="Session created")
    return render_template("error.html", error_content=error_content_500)


@main_blueprint.route("/status", methods=["GET"])
def status() -> tuple[str, int]:
    """Status check endpoint.

    :return: Empty 200 response.
    """
    logger.info("Status check hit")
    return "", 200
