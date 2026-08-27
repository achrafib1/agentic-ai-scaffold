import subprocess
from unittest.mock import patch

import pytest

from agentic_ai_scaffold.shell import run_command


def test_run_command_does_not_invoke_a_shell() -> None:
    with patch("agentic_ai_scaffold.shell.subprocess.run") as run:
        run_command(["uv", "init", "support-agent"], cwd="workspace")

    run.assert_called_once_with(
        ["uv", "init", "support-agent"],
        cwd="workspace",
        shell=False,
        check=True,
        text=True,
        capture_output=True,
    )


def test_run_command_exits_when_the_process_fails() -> None:
    failure = subprocess.CalledProcessError(1, ["uv", "sync"], stderr="failed")
    with (
        patch("agentic_ai_scaffold.shell.subprocess.run", side_effect=failure),
        pytest.raises(SystemExit),
    ):
        run_command(["uv", "sync"])
