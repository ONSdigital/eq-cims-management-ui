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

import requests
from flask import (
    Blueprint,
    Response,
    current_app,
    redirect,
    render_template,
    request,
    url_for,
)
from flask.typing import ResponseReturnValue
from flask_socketio import emit, join_room
from google.api_core.exceptions import RetryError

from eq_cims_management_ui.errors.routes import error_content_500
from eq_cims_management_ui.utils.database.application_logic import (
    create_new_session,
    get_collection_instruments,
    get_session_status,
    is_latest_session_in_progress,
    update_ci_status,
    update_session_status,
)
from eq_cims_management_ui.utils.socketio import socketio

main_blueprint = Blueprint("main", __name__)
view_session_blueprint = Blueprint(
    name="view_session",
    import_name=__name__,
)

logger = logging.getLogger(__name__)

STATUS_TO_SUFFIX = {"Started": "info", "Success": "success", "Failure": "error", "Not Started": "dead"}


@main_blueprint.before_request
def before_request_func() -> None:
    """Log the request before it is processed."""
    if request.endpoint != "status":
        logger.info("Request received for %s", request.url)


@socketio.on("connect")
def handle_connect(auth):
    """Create a new Websocket session and join the room for the session."""
    session_id = auth.get("session_id")
    current_app.config["session_id"] = session_id
    if session_id:
        join_room(session_id)


def emit_status(guid, ci_status, session_id):
    """Emit the status of a collection instrument and update the status in the database."""
    emit(
        "cell_update",
        {"guid": guid, "status": ci_status, "index": 5, "suffix": STATUS_TO_SUFFIX[ci_status]},
        to=session_id,
    )
    update_ci_status(guid, ci_status)


@socketio.on("republish")
def handle_republish():
    """
    Republish the collection instruments and emit the status to the Websocket session depending on the response
    from Author republish API.
    """
    session_id = current_app.config.get("session_id")
    ci_metadata = get_collection_instruments()
    update_session_status("Running")
    emit("button_disable", to=session_id)

    for ci in ci_metadata:
        guid = ci["cir_id"]
        if ci["status"] == "Success":
            emit_status(guid, "Success", session_id)
            continue

        emit_status(guid, "Started", session_id)
        try:
            response = requests.get(
                f"http://localhost:8081/republishschema/{guid}/cirversion/{ci['cir_version']}",
                timeout=10000,
            )
            ci_status = "Success" if response.json()["success"] else "Failure"
        except (requests.exceptions.ConnectionError, ConnectionRefusedError):
            logger.exception("Failed to republish CI: %s", guid)
            ci_status = "Failure"

        logger.error("%s republished CI: %s", "Successfully" if ci_status == "Success" else "Failed to", guid)
        emit_status(guid, ci_status, session_id)

    updated_ci_metadata = get_collection_instruments()
    if all(ci["status"] == "Success" for ci in updated_ci_metadata):
        update_session_status("Success")
    else:
        update_session_status("Failure")
        emit("button_enable", to=session_id)


@main_blueprint.route("/", methods=["GET"])
def index() -> Response | ResponseReturnValue:
    """
    Retrieve UI index and checks if there is a session already present.

    Returns:
        Response: A redirect to the view-session page if a session is already present.
        ResponseReturnValue: 200 index page.
    """
    if is_latest_session_in_progress():
        return redirect(url_for("main.get_view_session"))
    return render_template("index.html")


@main_blueprint.route("/create-session", methods=["GET"])
def create_session() -> Response | ResponseReturnValue:
    """
    Create a new session in the Firestore database and redirect to the view-session page.

    Returns:
        Response: A redirect to the view-session page if the session is created successfully.
        ResponseReturnValue: An error page with a 500 status code indicating that the session couldn't be created.

    Raises:
        RetryError: If there is an error while creating the session in the database, a RetryError is raised.
    """
    if is_latest_session_in_progress():
        logger.info("Session already in progress, redirecting to view-session")
        return redirect(url_for("main.get_view_session"))

    try:
        create_new_session()
        return redirect(url_for("main.get_view_session"))
    except (RetryError, requests.exceptions.ConnectionError, ValueError):
        return render_template("error.html", error_content=error_content_500), 500


@main_blueprint.route("/status", methods=["GET"])
def status() -> ResponseReturnValue:
    """
    Status check endpoint.

    :return: Empty 200 response.
    """
    logger.info("Status check hit")
    return "", 200


@main_blueprint.route("/view-session", methods=["GET"])
def get_view_session() -> ResponseReturnValue:
    """
    Gets the collection instrument metadata from the database and renders the view-session page.

    Returns:
        ResponseReturnValue: The rendered view-session page.
        ResponseReturnValue: An error page with a 500 status code if no ci_metadata or Firestore session is present.

    Raises:
        AttributeError: As there's no ci_metadata or Firestore session present, an AttributeError is raised if the user
        tries to access the view-session page directly.
    """
    try:
        ci_metadata = get_collection_instruments()
        return render_template("view-session.html", ci_metadata=ci_metadata, session_status=get_session_status())
    except AttributeError:
        return render_template("error.html", error_content=error_content_500), 500
