"""Routes for the EQ CIR Management UI."""

import logging

from flask import (
    Blueprint,
    render_template,
    request,
)

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


@main_blueprint.route("/status", methods=["GET"])
def status() -> tuple[str, int]:
    """Status check endpoint.

    :return: Empty 200 response.
    """
    logger.info("Status check hit")
    return "", 200
