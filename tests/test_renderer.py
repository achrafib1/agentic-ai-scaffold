import tomllib
from pathlib import Path

import pytest

from agentic_ai_scaffold.config_types import (
    DatabaseChoice,
    ObservabilityChoice,
    ProjectConfiguration,
)
from agentic_ai_scaffold.renderer import TemplateRenderer


def configuration(*, database: DatabaseChoice, include_pre_commit: bool) -> ProjectConfiguration:
    return ProjectConfiguration(
        project_name="support-agent",
        python_version="3.12",
        database=database,
        include_mcp=False,
        observability=ObservabilityChoice.NONE,
        include_pre_commit=include_pre_commit,
    )


@pytest.mark.parametrize("include_pre_commit", [False, True])
def test_base_template_renders_valid_development_dependencies(tmp_path: Path, include_pre_commit: bool) -> None:
    renderer = TemplateRenderer(
        configuration(
            database=DatabaseChoice.NONE,
            include_pre_commit=include_pre_commit,
        )
    )

    renderer.render_overlay("base", str(tmp_path))

    pyproject = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")
    assert '"langchain-google-genai>=2.0.0"' in pyproject
    assert ('"pre-commit>=4.0.0"' in pyproject) is include_pre_commit


def test_sqlalchemy_overlay_generates_models_package(tmp_path: Path) -> None:
    renderer = TemplateRenderer(
        configuration(
            database=DatabaseChoice.SQLALCHEMY,
            include_pre_commit=False,
        )
    )

    renderer.render_overlay("extensions/db_sqlalchemy", str(tmp_path))

    models_package = tmp_path / "src/shared/infrastructure/db/models/__init__.py"
    assert models_package.is_file()
    assert "SQLAlchemy persistence models" in models_package.read_text(encoding="utf-8")


def test_pre_commit_overlay_is_explicit(tmp_path: Path) -> None:
    renderer = TemplateRenderer(
        configuration(
            database=DatabaseChoice.NONE,
            include_pre_commit=True,
        )
    )

    renderer.render_overlay("base", str(tmp_path))
    assert not (tmp_path / ".pre-commit-config.yaml").exists()

    renderer.render_overlay("extensions/quality_pre_commit", str(tmp_path))
    assert (tmp_path / ".pre-commit-config.yaml").is_file()


@pytest.mark.parametrize(
    ("database", "include_mcp", "observability", "include_pre_commit"),
    [
        (DatabaseChoice.NONE, False, ObservabilityChoice.NONE, False),
        (DatabaseChoice.SQLALCHEMY, True, ObservabilityChoice.OPIK, True),
    ],
)
def test_rendered_option_boundaries_are_syntactically_valid(
    tmp_path: Path,
    database: DatabaseChoice,
    include_mcp: bool,
    observability: ObservabilityChoice,
    include_pre_commit: bool,
) -> None:
    renderer = TemplateRenderer(
        ProjectConfiguration(
            project_name="support-agent",
            python_version="3.12",
            database=database,
            include_mcp=include_mcp,
            observability=observability,
            include_pre_commit=include_pre_commit,
        )
    )
    renderer.render_overlay("base", str(tmp_path))
    if database == DatabaseChoice.SQLALCHEMY:
        renderer.render_overlay("extensions/db_sqlalchemy", str(tmp_path))
    if include_mcp:
        renderer.render_overlay("extensions/mcp_server", str(tmp_path))
    if observability == ObservabilityChoice.OPIK:
        renderer.render_overlay("extensions/obs_opik", str(tmp_path))
    if include_pre_commit:
        renderer.render_overlay("extensions/quality_pre_commit", str(tmp_path))

    with (tmp_path / "pyproject.toml").open("rb") as pyproject:
        tomllib.load(pyproject)

    for python_file in tmp_path.rglob("*.py"):
        source = python_file.read_text(encoding="utf-8")
        compile(source, str(python_file), "exec")

    readme = (tmp_path / "README.md").read_text(encoding="utf-8")
    assert ("## Persistence models" in readme) is (database == DatabaseChoice.SQLALCHEMY)
    assert ("## Observability" in readme) is (observability == ObservabilityChoice.OPIK)
