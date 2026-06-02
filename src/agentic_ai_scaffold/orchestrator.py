# Path: src/agentic_ai_scaffold/orchestrator.py
"""
The Orchestrator coordinates the entire scaffolding process.

It dictates the order of operations: environment pre-checks (verifying/installing uv),
workspace initialization, virtual environment setup, template rendering, and dependency resolution.
"""

import os
from pathlib import Path
import sys

import questionary
from rich.console import Console
from rich.panel import Panel

from agentic_ai_scaffold.config_types import (
    DatabaseChoice,
    ObservabilityChoice,
    ProjectConfiguration,
)
from agentic_ai_scaffold.renderer import TemplateRenderer
from agentic_ai_scaffold.shell import run_command, is_uv_installed, install_uv_via_pip

console = Console()


class ScaffoldOrchestrator:
    """Executes the scaffolding workflow based on the provided configuration."""

    def __init__(self, config: ProjectConfiguration):
        """
        Initializes the orchestrator.

        Args:
            config (ProjectConfiguration): The validated configuration from the CLI.
        """
        self.config = config
        self.target_dir = Path(os.getcwd()) / self.config.project_name
        self.renderer = TemplateRenderer(self.config)

    def build_project(self) -> None:
        """
        Executes the build pipeline. Uses Rich status spinners for a premium user experience.
        """
        # 1. PRE-CHECK: Ensure 'uv' is available before making any folders
        self._verify_or_install_uv()

        console.print(
            f"\n[bold green]🏗️  Forging Project:[/bold green] [cyan]{self.config.project_name}[/cyan]\n"
        )

        with console.status(
            "[bold blue]Initializing workspace and Python environment...[/bold blue]",
            spinner="dots",
        ):
            self._initialize_workspace()

        with console.status(
            "[bold blue]Setting up local virtual environment (.venv)...[/bold blue]",
            spinner="dots",
        ):
            self._setup_virtual_environment()

        with console.status(
            "[bold blue]Rendering architectural templates...[/bold blue]",
            spinner="dots",
        ):
            self._render_templates()

        with console.status(
            "[bold blue]Resolving dependencies via uv...[/bold blue]", spinner="dots"
        ):
            self._install_dependencies()

        with console.status(
            "[bold blue]Finalizing git and pre-commit hooks...[/bold blue]",
            spinner="dots",
        ):
            self._finalize_setup()

        self._print_success_summary()

    def _verify_or_install_uv(self) -> None:
        """
        Verifies if uv is installed. If missing, guides the user to install it
        manually or attempts to install it automatically via pip.
        """
        if is_uv_installed():
            return

        console.print(
            Panel(
                "[bold yellow]⚠️ 'uv' package manager not found on your system PATH![/bold yellow]\n\n"
                "'uv' is an ultra-fast Rust-based package manager required by this scaffolding engine.",
                title="System Requirements",
                border_style="yellow",
            )
        )

        install_choice = questionary.confirm(
            "Would you like 'agentic-ai-scaffold' to install 'uv' automatically via pip now?",
            default=True,
        ).ask()

        if install_choice:
            with console.status(
                "[bold green]Installing uv...[/bold green]", spinner="dots"
            ):
                success = install_uv_via_pip()
            if success:
                console.print(
                    "[bold green]✅ 'uv' installed successfully![/bold green]\n"
                )
                return

        # If installation fails or is declined, provide manual setup instructions
        console.print(
            Panel(
                "[bold red]❌ Scaffolding aborted. 'uv' must be installed manually to proceed.[/bold red]\n\n"
                "[bold yellow]How to install uv:[/bold yellow]\n"
                '• Windows (CMD):   [cyan]powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"[/cyan]\n'
                "• macOS/Linux:     [cyan]curl -LsSf https://astral.sh/uv/install.sh | sh[/cyan]\n"
                "• Via pip:         [cyan]pip install uv[/cyan]",
                title="Manual Setup Guide",
                border_style="red",
            )
        )
        sys.exit(1)

    def _initialize_workspace(self) -> None:
        """Creates the directory and initializes uv."""
        self.target_dir.mkdir(parents=True, exist_ok=True)
        run_command(
            f"uv init {self.config.project_name}", cwd=str(self.target_dir.parent)
        )
        run_command(
            f"uv python pin {self.config.python_version}", cwd=str(self.target_dir)
        )

    def _setup_virtual_environment(self) -> None:
        """Explicitly builds the .venv virtual environment inside the target folder."""
        run_command("uv venv", cwd=str(self.target_dir))

    def _render_templates(self) -> None:
        """Applies the base template and any selected extensions."""
        # 1. Base Overlay
        self.renderer.render_overlay("base", str(self.target_dir))

        # 2. Database Overlay
        if self.config.database == DatabaseChoice.SQLALCHEMY:
            self.renderer.render_overlay(
                "extensions/db_sqlalchemy", str(self.target_dir)
            )

        # 3. MCP Server Overlay
        if self.config.include_mcp:
            self.renderer.render_overlay("extensions/mcp_server", str(self.target_dir))

        # 4. Observability Overlay
        if self.config.observability == ObservabilityChoice.OPIK:
            self.renderer.render_overlay("extensions/obs_opik", str(self.target_dir))

    def _install_dependencies(self) -> None:
        """Installs the locked dependencies."""
        run_command("uv sync", cwd=str(self.target_dir))

    def _finalize_setup(self) -> None:
        """Initializes Git and sets up pre-commit hooks."""
        run_command("git init", cwd=str(self.target_dir))

        if self.config.include_pre_commit:
            # We explicitly add pre-commit and ruff to development dependencies
            run_command("uv add --dev pre-commit ruff", cwd=str(self.target_dir))
            # Now uv can safely run it inside the project context!
            run_command("uv run pre-commit install", cwd=str(self.target_dir))

    def _print_success_summary(self) -> None:
        """Prints the final success screen to the user."""
        console.print(
            "\n[bold green]✨ Project successfully scaffolded! ✨[/bold green]\n"
        )
        console.print(f"👉 [bold cyan]cd {self.config.project_name}[/bold cyan]")
        console.print(
            f"👉 [bold cyan]Activate environment: .venv\\Scripts\\activate[/bold cyan] (Windows cmd)"
        )
        console.print("👉 [bold cyan]uv sync[/bold cyan]")
        console.print("\n[dim]Happy coding! Building the future of AI Agents.[/dim]\n")
