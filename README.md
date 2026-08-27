# Agentic AI Scaffold

An interactive Python CLI for generating a modular FastAPI and LangGraph
starter project. Optional template overlays add asynchronous SQLAlchemy
infrastructure, a FastMCP tool server example, Opik configuration helpers, and
pre-commit hooks without duplicating the base scaffold.

> [!IMPORTANT]
> This project is an early-stage scaffold and reference implementation. It
> creates a useful starting structure, but generated applications still require
> product-specific security, persistence models, deployment configuration, and
> integration testing before production use.

## What it generates

Every generated project includes:

- a FastAPI application with a health endpoint and versioned webhook route;
- a LangGraph conversation graph backed by Groq or Gemini adapters;
- typed, environment-based configuration with Pydantic Settings;
- a `uv`-managed Python project and local virtual environment;
- Ruff development tooling and a small Makefile command surface; and
- a generated README that reflects the selected options.

The interactive wizard can also add:

| Option | Generated capability | Current status |
| --- | --- | --- |
| SQLAlchemy | Async engine, session dependency, declarative base, and `models` package | Implemented; migrations and application models are not generated |
| FastMCP | A standalone stdio server and example system-time tool | Server implemented; agent-side transport is demonstration-only |
| Opik | Configuration and tracing helper module | Helper implemented; applications must initialize and apply it |
| Pre-commit | Ruff hooks and reproducible development dependencies | Implemented |

SQLModel, MongoDB, and Phoenix appear as planned choices in the CLI and exit
without generating a project.

## Architecture

The CLI separates project coordination from file generation:

```text
CLI prompts
    │
    ▼
ProjectConfiguration
    │
    ▼
ScaffoldOrchestrator ──► uv / Git commands
    │
    ▼
TemplateRenderer
    ├── base template
    └── selected extension overlays
            │
            ▼
      generated project
```

Templates are regular files under `templates/`. Extension directories mirror
the generated project layout, so an overlay can add or replace files without
placing generated source code inside Python strings.

See [Architecture](docs/architecture.md) for component boundaries and the
generated request flow. See [Extending the scaffold](docs/extending.md) for the
overlay contract.

## Requirements

- Python 3.12 or newer
- [`uv`](https://docs.astral.sh/uv/)
- Git, because generated projects are initialized as local repositories

Generated applications require provider credentials only when their external
LLM or observability integrations are exercised.

## Installation

Clone the repository and synchronize its development environment:

```bash
git clone <repository-url>
cd agentic-ai-scaffold
uv sync
```

Run the CLI from the checkout:

```bash
uv run agentic-scaffold --help
uv run agentic-scaffold create
```

To expose the command as an isolated local tool:

```bash
uv tool install .
agentic-scaffold --help
```

Project names may contain letters, numbers, hyphens, and underscores and must
start with a letter. The project is created beneath the current directory.

## Scaffold workflow

During `create`, the CLI asks for:

1. a project name and Python version;
2. a database option;
3. whether to include the MCP server;
4. an observability option; and
5. whether to install pre-commit hooks.

After confirmation, the orchestrator creates the project, pins Python, renders
the selected overlays, resolves dependencies with `uv sync`, initializes Git,
and installs the hook when selected. External command arguments are passed
directly to subprocesses rather than through a command shell.

## Generated layout

```text
generated-project/
├── .env.example
├── .pre-commit-config.yaml     # optional
├── Makefile
├── README.md
├── pyproject.toml
└── src/
    ├── main.py
    ├── app/
    │   ├── agent/              # LangGraph state, nodes, edges, and graph
    │   ├── gateway/            # FastAPI v1 routing and webhook ingestion
    │   └── mcp_server/         # optional FastMCP server
    └── shared/
        ├── domain/             # application configuration and domain types
        └── infrastructure/
            ├── db/             # optional SQLAlchemy infrastructure/models
            └── observability/  # optional Opik helpers
```

SQLAlchemy mappings belong in
`src/shared/infrastructure/db/models`. Keeping ORM mappings in infrastructure
avoids coupling pure domain types to a persistence framework.

## Development

The repository currently configures Ruff and pytest:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

Build both distribution formats with:

```bash
uv build
```

The build configuration embeds the template tree in the wheel while preserving
the checkout layout used during development.

## Security considerations

- Never commit generated `.env` files or real provider credentials.
- Values in `.env.example` are placeholders and are not usable secrets.
- The generated webhook is unauthenticated by default. Add authentication,
  authorization, rate limiting, payload limits, and channel signature
  verification for the intended deployment.
- The background task runs in the API process. Use a durable queue when work
  must survive restarts or scale across processes.
- Review dependency versions, CORS origins, logging, and error reporting for
  the target environment.

## Known limitations

- The MCP client wrapper returns a local fallback tool instead of connecting to
  the generated MCP server.
- Opik initialization and tracing decorators are provided but not wired into
  the application lifecycle or graph nodes.
- SQLAlchemy support does not include Alembic or example tables.
- Agent responses are logged by the background task but are not returned to a
  channel or stored.
- The generated graph has no durable LangGraph checkpointer.
- Generated application behavior is not yet covered by end-to-end tests.

## Roadmap

- Connect the LangGraph tool path to the generated MCP transport.
- Add an optional Alembic overlay and model-discovery convention.
- Add authenticated gateway and channel-adapter examples.
- Add durable job processing and conversation persistence options.
- Add rendered-project smoke tests across supported option combinations.
- Implement or remove the placeholder database and observability choices.

## Contributing

Keep the base template small and introduce optional capabilities as overlays.
Changes should include tests that render affected option combinations and must
not introduce credentials or machine-specific output. Run the documented
quality checks before opening a change.

This repository does not currently declare a license. Until one is added, no
open-source usage rights should be assumed.
