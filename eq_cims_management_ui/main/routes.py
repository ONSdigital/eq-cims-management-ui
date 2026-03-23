"""Routes for the EQ CIR Management UI."""

import logging
import time

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for
)

main_blueprint = Blueprint("main", __name__)

logger = logging.getLogger(__name__)


@main_blueprint.before_request
def before_request_func() -> None:
    """Log the request before it is processed."""
    if request.endpoint != "status":
        message = "Request received"
        logger.info(message)


@main_blueprint.route("/", methods=["GET", "POST"])
def index():
    """Common URL defaults.

    :return: 301 redirect to start page.
    """

    if request.method == "GET":
        return render_template("index.html")

    else:
        # to be replaced by CIR and DB session calls
        time.sleep(3)

        return redirect(
                        url_for(
                            "main.view_session"
                        )
                    )
    

@main_blueprint.route("/view-session", methods=["GET", "POST"])
def view_session():

    if request.method == "GET":
        return render_template("view-session.html")

    else:

        return redirect(
                        url_for(
                            "main.migrating"
                        )
                    )


@main_blueprint.route("/migrating", methods=["GET", "POST"])
def migrating():

    return render_template("migrating.html")


@main_blueprint.route("/ci-status/<guid>", methods=["GET"])
def ci_status(guid):

    return render_template("ci-status.html", guid=guid)


@main_blueprint.route("/status", methods=["GET"])
def status() -> tuple[str, int]:
    """Status check endpoint.

    :return: Empty 200 response.
    """
    logger.info("Status check hit")
    return "", 200
