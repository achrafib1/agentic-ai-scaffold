# Path: src/agentic_ai_scaffold/renderer.py
"""
Template rendering engine utilizing Jinja2.

Responsible for reading `.j2` files, injecting dynamic configuration variables,
and writing physical `.py` files into the newly created project directory.
Dynamically resolves template paths relative to the installed package location.
"""

import os
import shutil
from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader

from agentic_ai_scaffold.config_types import ProjectConfiguration


class TemplateRenderer:
    """Handles the parsing and rendering of project templates."""

    def __init__(self, config: ProjectConfiguration):
        """
        Initializes the TemplateRenderer.
        Dynamically resolves the absolute path to the templates folder relative to this file.

        Args:
            config (ProjectConfiguration): The user's configuration choices.
        """
        self.config = config

        # PRO PATH RESOLUTION:
        # We need to go up exactly 3 levels to reach the PROJECT_ROOT (File -> Module -> Src -> Root)
        # parents[0] = src/agentic_ai_scaffold/
        # parents[1] = src/
        # parents[2] = PROJECT_ROOT/ (The nested Git Repo root where 'templates' lives)
        cli_root = Path(__file__).resolve().parents[2]
        self.template_base_dir = (cli_root / "templates").resolve()

        # Fail early and informatively if the templates directory is missing
        if not self.template_base_dir.exists():
            raise FileNotFoundError(
                f"Templates directory not found at: {self.template_base_dir}\n"
                f"Please ensure the 'templates' folder exists in your cloned repository."
            )

        # Convert dataclass to dictionary for Jinja2 context
        self.context: Dict[str, Any] = {
            "project_name": self.config.project_name,
            "python_version": self.config.python_version,
            "has_db": self.config.database.value != "none",
            "has_mcp": self.config.include_mcp,
            "has_observability": self.config.observability.value != "none",
        }

    def render_overlay(self, overlay_path: str, destination_dir: str) -> None:
        """
        Copies a specific template overlay (e.g., 'base' or 'extensions/db_sqlalchemy')
        to the target destination, parsing any `.j2` files it encounters.

        Args:
            overlay_path (str): The path to the overlay inside the templates directory.
            destination_dir (str): The absolute path where the project is being built.
        """
        source_dir = self.template_base_dir / overlay_path

        if not source_dir.exists():
            return  # Fail gracefully if an extension template doesn't exist yet

        env = Environment(
            loader=FileSystemLoader(str(source_dir)), keep_trailing_newline=True
        )

        for root, dirs, files in os.walk(source_dir):
            relative_root = Path(root).relative_to(source_dir)
            target_root = Path(destination_dir) / relative_root

            # Ensure target directory exists
            target_root.mkdir(parents=True, exist_ok=True)

            for file_name in files:
                source_file = Path(root) / file_name

                # If it's a Jinja template, render it and strip the .j2 extension
                if file_name.endswith(".j2"):
                    target_file = target_root / file_name[:-3]

                    # PRO WINDOWS FIX: Convert the template path to POSIX format (using forward slashes)
                    # because Jinja2's FileSystemLoader strictly requires forward slashes on all OS platforms.
                    template_path = (relative_root / file_name).as_posix()
                    template = env.get_template(template_path)

                    rendered_content = template.render(**self.context)

                    with open(target_file, "w", encoding="utf-8") as f:
                        f.write(rendered_content)
                else:
                    # If it's a standard file (like an image or basic text), just copy it
                    target_file = target_root / file_name
                    shutil.copy2(source_file, target_file)
