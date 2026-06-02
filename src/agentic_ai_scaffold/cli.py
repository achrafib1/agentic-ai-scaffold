# Path: src/agentic_ai_scaffold/cli.py
"""
Command Line Interface entry point.

Utilizes Typer for flag parsing and Questionary for rich interactive terminal prompts.
Supports multiple subcommands by explicitly registering a 'create' and a 'version' command.
"""

import sys

import questionary
import typer
from rich.console import Console
from rich.panel import Panel

from agentic_ai_scaffold.config_types import (
    DatabaseChoice,
    ObservabilityChoice,
    ProjectConfiguration,
)
from agentic_ai_scaffold.orchestrator import ScaffoldOrchestrator

# Initialize the Typer app. We enforce no_args_is_help so it shows the help screen if run empty.
app = typer.Typer(
    help="Agentic AI Scaffold: Enterprise Agent Architecture Generator",
    no_args_is_help=True,
)
console = Console()


@app.command(name="create")
def create() -> None:
    """
    Interactively guides the user through scaffolding a new Enterprise AI Agent project.
    """
    console.print(
        Panel.get_singleton().fit(
            "[bold cyan]🤖 Welcome to Agentic AI Scaffold[/bold cyan]\n"
            "[dim]The enterprise standard for building modular, scalable AI Agent backends.[/dim]",
            border_style="cyan",
        )
        if hasattr(Panel, "get_singleton")
        else Panel.fit(
            "[bold cyan]🤖 Welcome to Agentic AI Scaffold[/bold cyan]\n"
            "[dim]The enterprise standard for building modular, scalable AI Agent backends.[/dim]",
            border_style="cyan",
        )
    )

    try:
        # Interactive Prompting
        project_name = questionary.text(
            "What is the name of your project?",
            validate=lambda text: len(text) > 0 or "Project name cannot be empty.",
        ).ask()

        python_version = questionary.text(
            "Which Python version should uv pin?", default="3.12"
        ).ask()

        db_raw = questionary.select(
            "Which Database ORM do you want to configure?",
            choices=[e.value for e in DatabaseChoice],
        ).ask()

        # Handle 'Coming Soon' selections gracefully
        if "Coming Soon" in db_raw:
            console.print(
                f"\n[bold yellow]⚠️ {db_raw} is currently in development. Exiting.[/bold yellow]"
            )
            sys.exit(0)

        include_mcp = questionary.confirm(
            "Do you want to include a standalone FastMCP Tool Server?", default=True
        ).ask()

        obs_raw = questionary.select(
            "Which AI Observability platform do you want to configure?",
            choices=[e.value for e in ObservabilityChoice],
        ).ask()

        if "Coming Soon" in obs_raw:
            console.print(
                f"\n[bold yellow]⚠️ {obs_raw} is currently in development. Exiting.[/bold yellow]"
            )
            sys.exit(0)

        include_pre_commit = questionary.confirm(
            "Include .pre-commit-config.yaml for automated code formatting (Ruff)?",
            default=True,
        ).ask()

        # Compile the configuration
        config = ProjectConfiguration(
            project_name=project_name,
            python_version=python_version,
            database=DatabaseChoice(db_raw),
            include_mcp=include_mcp,
            observability=ObservabilityChoice(obs_raw),
            include_pre_commit=include_pre_commit,
        )

        # Trigger the Orchestrator
        orchestrator = ScaffoldOrchestrator(config)
        orchestrator.build_project()

    except KeyboardInterrupt:
        console.print("\n[bold red]❌ Scaffolding aborted by user.[/bold red]")
        sys.exit(1)


@app.command(name="version")
def version() -> None:
    """
    Displays the current version of the agentic-ai-scaffold tool.
    """
    console.print(
        "[bold cyan]Agentic AI Scaffold CLI[/bold cyan] version: [bold green]0.1.0[/bold green]"
    )


if __name__ == "__main__":
    app()
