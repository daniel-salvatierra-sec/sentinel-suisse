# Sentinel Suisse

Swiss housing and job listing aggregator with multi-channel alerts (WhatsApp, email).

Personal project built with **secure-by-design** methodology: each phase closes with a security checklist and evidence before moving on.

## Phase documentation

Detailed step-by-step reports (suitable for Google Docs / portfolio) live in [`docs/phases/`](docs/phases/).

| Phase | Status | Document |
|-------|--------|----------|
| 0 — Secure environment | Complete | [phase-0-secure-environment.md](docs/phases/phase-0-secure-environment.md) |
| 1 — Data model | Complete | [phase-1-data-model.md](docs/phases/phase-1-data-model.md) |
| 2 — Internal CRUD | Complete | [phase-2-internal-crud.md](docs/phases/phase-2-internal-crud.md) |

## Requirements

- Python 3.11+
- Git
- Docker Desktop (Postgres + Redis for Phase 1+)
- pre-commit (via dev dependencies)

## Quick start

```powershell
cd C:\Users\danin\Projects\sentinel-suisse
.\.venv\Scripts\Activate.ps1
docker compose up -d
pip install -r requirements.txt
pre-commit run --all-files
```

## Project structure

```
sentinel-suisse/
├── src/sentinel_suisse/    # Application source
├── alembic/                # Database migrations
├── docs/phases/            # Phase completion reports
├── docs/privacy/           # nLPD / data mapping
├── docs/agent-prompts/     # Security prompts per phase
└── docker-compose.yml      # Postgres + Redis
```

## License

Private — personal use.
