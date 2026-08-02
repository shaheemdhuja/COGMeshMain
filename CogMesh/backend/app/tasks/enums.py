"""Enumerations for AI Task Adapter Layer."""

from enum import Enum


class TaskStatus(str, Enum):
    """Execution status of an AI task adapter run."""

    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    INVALID_INPUT = "INVALID_INPUT"
