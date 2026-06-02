# Path: src/agentic_ai_scaffold/shell.py
"""
Shell command execution utilities.

Provides robust wrappers around the subprocess module with rich logging,
cross-platform executable detection (via shutil), and automated installation scripts.
"""

import shutil
import subprocess
import sys
from typing import Optional

from rich.console import Console
from rich.panel import Panel

console = Console()


def is_uv_installed() -> bool:
    """
    Checks if the 'uv' executable is available in the system's PATH.

    Returns:
        bool: True if 'uv' is found, False otherwise.
    """
    return shutil.which("uv") is not None


def install_uv_via_pip() -> bool:
    """
    Attempts to install 'uv' into the current active Python environment using pip.

    Returns:
        bool: True if installation was successful, False otherwise.
    """
    try:
        # Run pip install uv using the active Python interpreter
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "uv"],
            check=True,
            capture_output=True,
            text=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]Installation failed:[/bold red] {e.stderr}")
        return False


def run_command(
    command: str, cwd: Optional[str] = None, hide_output: bool = True
) -> None:
    """
    Executes a shell command safely in a specified directory.

    Args:
        command (str): The shell command to execute.
        cwd (Optional[str]): The directory to execute the command in. Defaults to current.
        hide_output (bool): If True, suppresses standard output unless an error occurs.

    Raises:
        SystemExit: Exits the application gracefully if the command fails.
    """
    try:
        subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            check=True,
            text=True,
            capture_output=hide_output,
        )
    except subprocess.CalledProcessError as e:
        error_msg = f"[bold red]Command Failed:[/bold red] {command}\n\n[bold yellow]Error Output:[/bold yellow]\n{e.stderr}"
        console.print(Panel(error_msg, title="🚨 Execution Error", border_style="red"))
        sys.exit(1)
