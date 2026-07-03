"""This module contains the enumerators to reflect the status of the database."""

from enum import Enum


class Status(Enum):
    """An enumerator to reflect the status of the database."""

    NOT_STARTED = "Not started"
    RUNNING = "Running"
    SUCCESS = "Success"
    FAILURE = "Failure"

class CIStatus(Enum):
    """An enumerator to reflect the status of a collection instrument."""
    NOT_STARTED = "Not started"
    STARTED = "Started"
    SUCCESS = "Success"
    FAILURE = "Failure"
