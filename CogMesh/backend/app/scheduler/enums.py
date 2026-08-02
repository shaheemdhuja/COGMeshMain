"""Enumerations for the Adaptive Task Scheduler."""

from enum import Enum


class SchedulingStrategy(str, Enum):
    """Available scheduling heuristics."""

    WEIGHTED_SCORE = "WEIGHTED_SCORE"
    ROUND_ROBIN = "ROUND_ROBIN"
    BATTERY_HEAVY = "BATTERY_HEAVY"
