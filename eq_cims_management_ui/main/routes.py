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
import os

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
from flask_socketio import emit, join_room  # pyright: ignore
from google.api_core.exceptions import RetryError

from eq_cims_management_ui.errors.routes import error_content_404, error_content_500
from eq_cims_management_ui.utils.database.application_logic import (
    create_new_session,
    get_collection_instruments,
    get_session_status,
    is_latest_session_in_progress,
    update_ci_status,
    update_session_status,
)
from eq_cims_management_ui.utils.database.status import CIStatus, Status
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
def handle_connect(auth: dict) -> None:
    """Create a new Websocket session and join the room for the session."""
    session_id = auth.get("session_id")
    current_app.config["session_id"] = session_id
    if session_id:
        join_room(session_id)


def emit_status(guid: str, ci_status: str, session_id: str, validator_version: str, error_message: str) -> None:
    """Emit the status of a collection instrument and update the status in the database."""
    emit(
        "cell_update",
        {
            "guid": guid,
            "status": ci_status,
            "index": 5,
            "suffix": STATUS_TO_SUFFIX[ci_status],
            "validator_version": validator_version,
            "error_message": error_message,
        },
        to=session_id,
    )
    update_ci_status(guid, ci_status)


@socketio.on("republish")
def handle_republish() -> None:
    """
    Republish the collection instruments and emit the status to the Websocket session depending on the response
    from Author republish API.
    """
    session_id = current_app.config.get("session_id", "")
    ci_metadata = get_collection_instruments()
    update_session_status(Status.RUNNING.value)
    emit("button_disable", to=session_id)

    for ci in ci_metadata:
        guid = ci["cir_id"]
        if ci["status"] == CIStatus.SUCCESS.value:
            emit_status(guid, CIStatus.SUCCESS.value, session_id, ci["validator_version"], ci["error_message"])
            continue

        emit_status(guid, CIStatus.STARTED.value, session_id, ci["validator_version"], ci["error_message"])
        try:
            response = requests.get(
                f"http://{os.getenv("AUTHOR_REPUBLISH_API_URL")}/republishschema/{guid}/cirversion/{ci['cir_version']}",
                timeout=15,
            )
            ci_status = CIStatus.SUCCESS.value if response.json()["success"] else CIStatus.FAILURE.value
            logger.info("Successfully republished CI: %s", guid)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, KeyError, ValueError):
            ci_status = CIStatus.FAILURE.value
            logger.exception("Failed to republish CI: %s", guid)

        emit_status(guid, ci_status, session_id, ci["validator_version"], ci["error_message"])

    updated_ci_metadata = get_collection_instruments()
    if all(ci["status"] == CIStatus.SUCCESS.value for ci in updated_ci_metadata):
        update_session_status(Status.SUCCESS.value)
    else:
        update_session_status(Status.FAILURE.value)
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


@main_blueprint.route("/result/<guid>", methods=["GET"])
def get_result(guid: str) -> ResponseReturnValue:
    """
    Retrieves the metadata for a specific collection instrument which is then rendered on the result page.

    Args:
        guid: The unique identifier of the collection instrument.

    Returns:
        ResponseReturnValue: The rendered result page.
        ResponseReturnValue: An error page with a 404 status code if the collection instrument is not found.
    """
    ci_metadata = get_collection_instruments()

    ci = next((ci for ci in ci_metadata if ci["cir_id"] == guid), None)

    if not ci:
        return render_template("error.html", error_content=error_content_404, url="/view-session"), 404

    ci_status = ci["status"] if ci else "Not found"
    survey_id = ci["survey_id"] if ci else "Not found"
    form_type = ci["form_type"] if ci else "Not found"
    version = ci["cir_version"] if ci else "Not found"
    validator_version = ci["validator_version"] if ci else "Not found"
    error_message = ci["error_message"] if ci else "Not found"

    return render_template(
        "result.html",
        guid=guid,
        status=ci_status,
        survey_id=survey_id,
        form_type=form_type,
        version=str(version),
        validator_version=validator_version,
        error_message=error_message,
    )
