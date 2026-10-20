# FlowOS AI

FlowOS AI is an AI-native ERP and intelligent workspace for small and medium-sized apparel manufacturers. Version 0.1 targets a narrow, auditable workflow: order lookup → inventory gap analysis → purchase suggestion draft.

This repository currently contains the project foundation only. It does **not** include an LLM integration, production purchasing, arbitrary SQL, complete authorization, or multi-tenancy.

> Data safety: development, tests, documentation, screenshots, and demos must use synthetic data only. Never copy employer or customer data, source code, schemas, field names, status codes, API documents, or proprietary business rules into this repository or any third-party AI service.

## Repository layout

```text
backend/       FastAPI API, persistence, repositories, services, domain, migrations, tests
frontend/      React + TypeScript + Vite placeholder and planned structure
docs/          Product, business-rule, compliance, and architecture baselines
docker-compose.yml
```

## Start locally with Docker

```bash
cp .env.example .env
docker compose up --build
```

The API is then available at `http://localhost:8000`; verify it with:

```bash
curl http://localhost:8000/api/v1/health
```

Expected response:

```json
{"status":"ok","service":"flowos-api","version":"0.1.0"}
```

The API container runs versioned database migrations before starting the server.

Create idempotent synthetic development data with:

```bash
cd backend
uv run python -m app.commands.seed_synthetic
```

Business API endpoints currently available:

```text
GET /api/v1/sales-orders
GET /api/v1/sales-orders/{order_id}
GET /api/v1/sales-orders/{order_id}/material-requirements
GET /api/v1/sales-orders/{order_id}/shortage-analysis?snapshot_id={snapshot_id}
```

API errors use a stable envelope with `error.code`, `error.message`, and optional
`error.details`. Material requirements are calculated only for confirmed orders whose
lines explicitly select an active, effective BOM version.

Shortage analysis always references an explicit final inventory snapshot. It reports
included supply, excluded inbound supply, warnings, source requirement rows, and the
versioned calculation rules used for the result.

## Run backend checks locally with uv

Dependencies and the Python environment are managed by [uv](https://docs.astral.sh/uv/). The project targets Python 3.12.

```bash
cd backend
uv sync --extra dev
uv run pytest
uv run ruff check .
```

The project configures the Tsinghua PyPI mirror for `uv` and commits `backend/uv.lock` for reproducible installs.

Run migrations against the configured PostgreSQL database:

```bash
cd backend
uv run alembic upgrade head
```

Alembic records the current revision in `alembic_version`. Generate a migration draft after changing models with `uv run alembic revision --autogenerate -m "describe change"`, review it, and then apply it with `uv run alembic upgrade head`.

## Current boundaries

- SQLAlchemy models are persistence objects only.
- Pydantic schemas define API contracts.
- Repositories own database queries; services orchestrate use cases.
- Future inventory-gap calculations belong in `app/domain` and must remain pure Python without ORM dependencies.
- All sample data must be unmistakably synthetic.

See [architecture](docs/architecture.md), [V0.1 PRD](docs/prd-v0.1.md), [AI Manufacturing Operating System direction](docs/ai-manufacturing-os.md), [development plan](docs/development-plan.md), [business rules](docs/business-rules.md), and [data compliance](docs/data-compliance.md).

## Codex project continuity

- Repository instructions: [AGENTS.md](AGENTS.md)
- Confirmed decisions: [docs/decisions.md](docs/decisions.md)
- Concise roadmap: [docs/roadmap.md](docs/roadmap.md)
- Current task: [.codex-context/current-task.md](.codex-context/current-task.md)
- Cross-session handoff: [.codex-context/handoff.md](.codex-context/handoff.md)

At the start of a new conversation, read the applicable `AGENTS.md` and the two
`.codex-context` files, then verify the current Git status before continuing. When the
user says “准备切换新对话”, refresh both context files from actual repository and
validation evidence; never copy secrets or `.env` contents into them.
