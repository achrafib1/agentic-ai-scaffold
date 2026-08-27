# Extending the scaffold

Agentic AI Scaffold uses directory overlays to keep optional features separate
from the base project. An extension should introduce one coherent capability
and mirror the paths it needs in the generated project.

## Overlay contract

Given this template:

```text
templates/extensions/example/src/shared/infrastructure/example/client.py.j2
```

rendering `extensions/example` produces:

```text
src/shared/infrastructure/example/client.py
```

Files ending in `.j2` are rendered and lose that suffix. Other files are
copied unchanged. If an overlay produces the same path as the base template,
the overlay is applied later and replaces the base result.

## Adding an extension

1. Add the user-facing choice to `config_types.py` when a new selection is
   required.
2. Capture that choice in `ProjectConfiguration`.
3. Expose only the rendering context needed by the templates.
4. Add the mirrored template tree under `templates/extensions/<name>/`.
5. Apply the overlay in `_render_templates` after the base template.
6. Add conditional dependencies to the generated `pyproject.toml.j2`.
7. Update the generated README using the same Jinja condition.
8. Add a rendering test for both selected and unselected behavior.

Avoid registering unfinished choices as if they worked. If a choice remains
visible for roadmap purposes, the CLI must stop before creating a partial
project and the documentation must label it as planned.

## Template guidelines

- Keep domain types independent of infrastructure libraries where practical.
- Put SQLAlchemy mappings in `shared/infrastructure/db/models`.
- Keep secrets out of templates; use unmistakable placeholders in
  `.env.example`.
- Do not add dependencies for extensions that were not selected.
- Prefer a small runnable boundary over placeholder modules that claim an
  integration exists.
- Keep generated commands compatible with the dependencies and paths emitted
  by the same option combination.
- Document required application work and failure behavior.

## Verification

At minimum, render the affected overlay into pytest's temporary directory and
assert that required files, dependencies, and conditional omissions are
correct. Then run:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv build
```

For changes to runtime templates, add a generated-project smoke test when the
required services can be substituted safely. Never place real credentials in
fixtures, commands, or generated examples.
