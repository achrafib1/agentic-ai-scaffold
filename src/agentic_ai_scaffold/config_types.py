"""
Configuration types and Enums for the Agentic AI Scaffold engine.
Ensures strict type safety and defines the supported architectural choices.
"""

from dataclasses import dataclass
from enum import Enum


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
