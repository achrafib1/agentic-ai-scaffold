from agentic_ai_scaffold.config_types import validate_project_name


def test_accepts_safe_project_names() -> None:
    assert validate_project_name("support-agent") is True
    assert validate_project_name("support_agent_2") is True


def test_rejects_paths_and_shell_syntax() -> None:
    assert validate_project_name("../outside") is not True
    assert validate_project_name("agent && echo unsafe") is not True
    assert validate_project_name("1-agent") is not True
