# Architecture

This document describes the behavior implemented by Agentic AI Scaffold 0.1.0
and separates it from the responsibilities left to generated applications.

## CLI components

### Configuration

`src/agentic_ai_scaffold/config_types.py` defines the supported selections and
the `ProjectConfiguration` value passed through the build. Project-name
validation restricts names before they become directory or process arguments.

### Orchestration

`ScaffoldOrchestrator` owns side effects and their order:

1. verify that `uv` is available, with an optional pip installation path;
2. create and initialize the target project;
3. create its virtual environment;
4. render the base and selected overlays;
5. synchronize dependencies;
6. initialize a local Git repository; and
7. install pre-commit hooks when selected.

External commands are expressed as argument lists and executed without a
command shell. A command failure prints captured output and stops the workflow.
The build is not transactional: an interrupted or failed run can leave a
partially generated directory for inspection or manual removal.

### Rendering

`TemplateRenderer` resolves templates from one of two locations:

- `templates/` in a source checkout; or
- `agentic_ai_scaffold/templates/` in an installed wheel.

It walks an overlay, renders `.j2` files with Jinja2, removes the `.j2` suffix,
and copies other files unchanged. Overlays are applied after the base, so a
matching extension path replaces the earlier generated file.

The rendering context currently exposes:

| Variable | Meaning |
| --- | --- |
| `project_name` | Validated project directory and distribution name |
| `python_version` | Version passed to `uv python pin` |
| `has_db` | Whether a supported database extension was selected |
| `has_mcp` | Whether the MCP extension was selected |
| `has_observability` | Whether a supported observability extension was selected |
| `has_pre_commit` | Whether pre-commit tooling was selected |

## Generated application

The generated code follows a modular-monolith layout. This describes code
ownership, not independently deployable services.

- `app.gateway` owns HTTP transport and request validation.
- `app.agent` owns LangGraph state and execution.
- `app.mcp_server` is optional and owns the example FastMCP process.
- `shared.domain` holds framework-light shared application types and settings.
- `shared.infrastructure` owns database and observability integrations.

### Request flow

```text
POST /api/v1/webhooks/message
        │
        ├── validate GenericMessagePayload
        ├── return HTTP 202
        └── schedule an in-process background task
                    │
                    ▼
             LangGraph agent_app
                    │
                    ├── invoke configured chat model
                    ├── optionally execute local fallback tools
                    └── log the final text
```

The API does not persist the request or response, authenticate the caller, or
deliver the response to the originating channel. Those are application-level
integration responsibilities.

## Optional boundaries

### SQLAlchemy

The database overlay supplies an asynchronous PostgreSQL engine, session
factory, request-scoped session generator, declarative base, and a dedicated
`models` package. It performs a best-effort connection check during startup.

ORM mappings belong in `shared.infrastructure.db.models`; domain objects that
do not require SQLAlchemy belong in `shared.domain`. Migration configuration
and tables are intentionally not invented by the scaffold.

### MCP

The extension creates a runnable FastMCP stdio server with a system-time tool.
The agent-side wrapper currently supplies a local LangChain fallback tool. It
does not establish a transport connection to the server, so service separation
and remote tool discovery remain demonstration-only.

### Opik

The extension adds configuration fields plus initialization and decorator
helpers. Generated code does not invoke those helpers automatically. This
avoids claiming tracing coverage that the application has not explicitly
wired and tested.

## Packaging and verification

Hatchling builds the CLI package. Wheel configuration copies the top-level
template tree into the installed Python package, while an editable checkout
uses the original template directory.

Repository tests cover project-name validation, safe process invocation,
conditional development tooling, and rendering of the database model package.
They do not currently execute a fully generated application against external
providers or PostgreSQL.
