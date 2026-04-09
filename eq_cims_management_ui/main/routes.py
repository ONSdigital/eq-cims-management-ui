"""Routes for the EQ CIR Management UI."""

import logging

from flask import (
    Blueprint,
    render_template,
    redirect,
    request,
    Response,
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


@main_blueprint.route("/", methods=["GET", "POST"])
def index() -> str | Response | tuple[str, int]:
    """
    GET: Retrieve UI index.
    POST: Create a new session in the Firestore database.

    return: 
        str (GET request): 200 index page.
        Response (POST request): A rendered HTML page with a message indicating that the session was created.
        tuple[str, int] (POST request): An error page with a 500 status code indicating that the session could not be created.
    """
    if request.method == "POST":
        try:
            create_session()
            return redirect("/view-session")
        except RetryError:
            return render_template("error.html", error_content=error_content_500), 500
    return render_template("index.html")


@main_blueprint.route("/view-session", methods=["GET"])
def create_and_view_session() -> str | tuple[str, int]:
    """Creates a new session in the Firestore databases and returns a list of CIs to render on the page.

    Returns:
        str: A rendered HTML page with a message indicating that the session was created. Note: To be updated to
        return a rendered page with a list of CIs.
    """
    try:
        # create_session()
        return render_template("view-session.html")
    except RetryError:
        return render_template("error.html", error_content=error_content_500), 500


@main_blueprint.route("/status", methods=["GET"])
def status() -> tuple[str, int]:
    """Status check endpoint.

    :return: Empty 200 response.
    """
    logger.info("Status check hit")
    return "", 200


# @main_blueprint.route("/view-session", methods=["GET"])
# def view_session() -> str:
#     """Outputs a table containing CIs in the latest session created.

#     :return: 200 view-session page.
#     """
    
#     return render_template("view-session.html")

