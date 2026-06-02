# agentic-ai-scaffold

<!-- Path: README.md -->

# 🛠️ Agentic AI Scaffold

An enterprise-grade Command Line Interface (CLI) scaffolding engine designed to generate modular, scalable, and production-ready AI Agent backends.

This tool automates the creation of a modern **Modular Monolith** architecture, integrating **FastAPI** (for gateway requests), **LangGraph** (for stateful agent workflows), and **FastMCP** (for decoupled, scalable tool execution).

---

## 🌟 Key Architectural Decisions

Unlike basic starter templates, `agentic-ai-scaffold` enforces robust software engineering standards:

- **Dynamic Scaffolding (No Code-In-Strings):** Generated code templates reside in raw, easily-editable physical directory layers (`templates/`). The CLI uses a **Jinja2 Directory Walking Engine** to inject variables and compile code dynamically with 100% platform-agnostic POSIX pathing [2].
- **Decoupled Agentic Loop:** The generated gateway (FastAPI) is entirely separated from the reasoning engine (LangGraph). The gateway normalizes incoming payloads into an `OmniMessage` schema, meaning you can plug in WhatsApp, Telegram, or Discord gateways without rewriting your core agent logic.
- **Decoupled Tools via FastMCP:** All external integrations (database RAG, web scrapers, APIs) are built as separate tools on an isolated Model Context Protocol (MCP) server. Your LangGraph agent retrieves these dynamically at runtime, allowing you to update tool logic without restarting the state machine.
- **Asynchronous Database Core:** Utilizes `asyncio`, `asyncpg`, and SQLAlchemy Async sessions to support high-concurrency environments typical of asynchronous AI agents. Includes a production-grade, asynchronous **Alembic** migration setup out of the box.
- **Autonomous Virtual Environments:** The CLI automatically checks for the ultra-fast Rust-based package manager **`uv`**, prompts to install it if missing, pins your Python version, and builds a dedicated `.venv` in the target project.

---

## 🚀 Installation & Local Setup

### 1. Prerequisites

Ensure you have Python 3.12+ installed on your machine. The CLI tool is built to handle dependency management on both Windows CMD and Unix shells natively.

### 2. Global Installation

Navigate to your cloned `agentic-ai-scaffold` directory and install the CLI globally in editable mode:

```cmd
:: Windows CMD
cd C:\path\to\cloned\agentic-ai-scaffold
uv pip install -e .
```

```bash
# macOS/Linux
cd /path/to/cloned/agentic-ai-scaffold
uv pip install -e .
```

_(Installing in editable mode ensures any changes you make to your local templates are reflected globally instantenously)_

### 3. Generate a New Project

Navigate to an empty workspace folder and trigger the interactive generation wizard:

```cmd
agentic-scaffold create
```

---

## 🗳️ Interactive Configuration Choices

The wizard will guide you through building the exact architecture you need:

1.  **Project Name:** Sets the core metadata of your system.
2.  **Python Version:** Ppins your `uv` workspace to your selected Python runtime.
3.  **Database ORM:** Configures an asynchronous **SQLAlchemy Engine** and Async **Alembic** migration pipeline connected to your direct database connection.
4.  **FastMCP Server:** Generates a standalone tool server structure and embeds an MCP client wrapper into your LangGraph nodes.
5.  **AI Observability:** Integrates **Opik** tracing decorators, automatically capturing every LLM invocation, node transition, and tool call in your dashboard.
6.  **Pre-Commit Quality Gate:** Places a `.pre-commit-config.yaml` file into your root directory and automatically configures `Ruff` to format and lint your code before every Git commit.

---

## 📂 The Generated Project Structure

The scaffolding engine generates the following clean layout inside your target folder:

```text
generated-project/
├── .venv/                         # Automatically created virtual environment
├── pyproject.toml                 # uv Workspace configuration
├── .env.example                   # Custom configuration template
├── Makefile                       # Cross-platform developer scripts (install, run, format)
├── alembic.ini                    # Database migrations configuration (If DB chosen)
│
└── src/
    ├── shared/                    # 📦 Shared Domain & Infrastructure (Cross-cutting)
    │   ├── domain/                # Pydantic schemas, SQLAlchemy tables, custom exceptions
    │   └── infrastructure/        # db engines (sessions, dependencies), Opik tracing
    │
    └── app/                       # 🚀 Micro-applications
        ├── gateway/               # FastAPI Gateway (Lifespans, v1 routing, authentication)
        ├── agent/                 # LangGraph workflows, states, nodes, and conditional edges
        └── mcp_server/            # Standalone FastMCP Tool server (If MCP chosen)
```

---

## 🛠️ Extensibility (Strategy Design Pattern)

The CLI tool is engineered to allow painless upgrades. Because the CLI uses an **Overlay Extension Strategy**, you do not have to write complex `if/else` logic to add new database drivers or agent frameworks.

To add a new extension (e.g., MongoDB support):

1. Create a directory: `templates/extensions/db_mongo/`.
2. Add your physical, raw `.py.j2` files in the exact layout you want them inside the generated project.
3. Register your new choice inside `src/agentic_ai_scaffold/config_types.py`.
4. The orchestrator will dynamically detect, merge, and overlay your new template files on top of the base template without modifying any of the existing CLI engine code.

---

## 🧑‍💻 Contributing & Developer Commands

When editing the CLI package itself, always run code formatting checks before committing:

```cmd
:: Format code with Ruff
uv run ruff format .

:: Lint code with Ruff
uv run ruff check .
```

_Built as a modular standard for the modern AI Engineering Community._
