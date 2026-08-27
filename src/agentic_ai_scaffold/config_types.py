"""
Configuration types and Enums for the Agentic AI Scaffold engine.
Ensures strict type safety and defines the supported architectural choices.
"""

import re
from dataclasses import dataclass
from enum import Enum

PROJECT_NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")


def validate_project_name(value: str) -> bool | str:
    """Validate a project name before it is used as a directory or argument."""
    if not value:
        return "Project name cannot be empty."
    if not PROJECT_NAME_PATTERN.fullmatch(value):
        return "Use letters, numbers, hyphens, or underscores; start with a letter."
    return True


class DatabaseChoice(str, Enum):
    """Enumeration of supported Database ORMs."""

    SQLALCHEMY = "sqlalchemy"
    SQLMODEL = "sqlmodel (Coming Soon)"
    MONGO = "mongodb (Coming Soon)"
    NONE = "none"


class ObservabilityChoice(str, Enum):
    """Enumeration of supported AI Observability platforms."""

    OPIK = "opik"
    PHOENIX = "phoenix (Coming Soon)"
    NONE = "none"


@dataclass
class ProjectConfiguration:
    """
    Holds the complete state of the user's scaffolding choices.
    This configuration is passed to the Orchestrator and Jinja2 renderer.
    """

    project_name: str
    python_version: str
    database: DatabaseChoice
    include_mcp: bool
    observability: ObservabilityChoice
    include_pre_commit: bool
