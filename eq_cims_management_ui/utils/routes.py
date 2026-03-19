"""Routes for the EQ CIR Management UI utils."""

from typing import cast

from flask import Blueprint, Response, abort, current_app, send_from_directory

utils_blueprint = Blueprint("utils", __name__)


@utils_blueprint.route("/favicon.ico")
def favicon() -> Response:
    """Simulate a favicon request."""
    static_folder = cast(str, current_app.static_folder)
    return send_from_directory(static_folder, "favicon.ico", mimetype="image/vnd.microsoft.icon")


@utils_blueprint.route("/400")
def trigger_400() -> Response:
    """Simulate an unauthorized error."""
    abort(400)


@utils_blueprint.route("/401")
def trigger_401() -> Response:
    """Simulate an unauthorized error."""
    abort(401)


@utils_blueprint.route("/403")
def trigger_403() -> Response:
    """Simulate a forbidden error."""
    abort(403)


@utils_blueprint.route("/405")
def trigger_405() -> Response:
    """Simulate an method not allowed error."""
    abort(405)


@utils_blueprint.route("/500")
def trigger_500() -> Response:
    """Simulate an internal server error."""
    abort(500)
