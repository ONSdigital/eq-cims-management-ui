"""
This module contains the routes for the EQ CIR Management UI.

Functions:
    index
    create_session
    status
    get_view_session

Raises:
    RetryError
"""

import logging

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    url_for,
)
from google.api_core.exceptions import RetryError
from werkzeug.wrappers.response import Response

from eq_cims_management_ui.errors.routes import error_content_500
from eq_cims_management_ui.utils.database.firestore_logic import create_new_session

main_blueprint = Blueprint("main", __name__)
view_session_blueprint = Blueprint(
    name="view_session",
    import_name=__name__,
)

logger = logging.getLogger(__name__)


@main_blueprint.before_request
def before_request_func() -> None:
    """Log the request before it is processed."""
    if request.endpoint != "status":
        message = "Request received"
        logger.info(message)


@main_blueprint.route("/", methods=["GET"])
def index() -> str:
    """
    Retrieve UI index.

    Returns:
        str: 200 index page.
    """
    return render_template("index.html")


@main_blueprint.route("/create-session", methods=["GET"])
def create_session() -> Response | tuple[str, int]:
    """
    Create a new session in the Firestore database and redirect to the view-session page.

    Returns:
        Response: A redirect to the view-session page if the session is created successfully.
        tuple[str, int]: An error page with a 500 status code indicating that the session couldn't be created.

    Raises:
        RetryError: If there is an error while creating the session in the database, a RetryError is raised.
    """
    try:
        session_id = create_new_session()
        logger.info("Session created successfully: %s", session_id)
        return redirect(url_for("view_session.get_view_session"))
    except RetryError:
        return render_template("error.html", error_content=error_content_500), 500


@main_blueprint.route("/status", methods=["GET"])
def status() -> tuple[str, int]:
    """
    Status check endpoint.

    :return: Empty 200 response.
    """
    logger.info("Status check hit")
    return "", 200


@view_session_blueprint.route("/view-session", methods=["GET"])
def get_view_session() -> str:
    """
    Render a template for the view session page.

    Returns:
        str: A rendered HTML page containing a table of sample CIs.
    """
    return render_template("view-session.html")
