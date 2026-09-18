# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

CFR-search is a FastAPI REST API that scrapes and serves climbing competition results from the Russian Climbing Federation website (rusclimbing.ru / c-f-r.ru). Deployed to Vercel as a Python serverless function (see `vercel.json`, entrypoint `app/main.py`). Live docs: https://cfr-search.vercel.app/docs

## Commands

Activate the venv first: `venv\Scripts\activate` (PowerShell: `venv\Scripts\Activate.ps1`).

```bash
# Run dev server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# or: npm run dev

# Tests
python -m pytest -v                      # pytest, discovers app/tests (see pyproject.toml testpaths)
python -m pytest app/tests/parser_test.py -v -k test_parse_events   # single test
python -m pytest --cov=app --cov-report=term    # coverage (npm run test:coverage)
python app/tests/run_tests.py            # alternate unittest-based runner (discovers *test*.py)

# Lint / format
ruff check --fix app                     # npm run lint:ruff
pylint --load-plugins=pylint_fastapi_plugin app   # npm run lint:pylint
black app/                               # npm run link:black-fix
```

There is no single `npm run lint` that works as written — its script chains `black-fix`/`ruff`/`pylint` with a typo (missing `&&` after the first command), so run the three lint commands above individually.

## Architecture

Layered architecture, strictly one-directional: **endpoints → services → repositories → models**. Don't skip layers (e.g. don't query the DB directly from an endpoint).

- `app/api/v1/endpoints/*.py` — FastAPI routers (`events_router`, `teams_router`, both mounted under `/api` prefix). Endpoints depend on a service (via a local `get_*_service` dependency function that wraps `get_session`), catch exceptions, and wrap responses in `BaseResponse`/`BaseResponse[T]` (`schemas/event.py`).
- `app/services/*.py` — business logic. `EventService` both reads from the DB (via `EventRepository`) and fetches/parses events live from the external site (`requests` + BeautifulSoup, via `app/utils/parsers.py`), used by the `/events/fetch` endpoint. `TeamService` scrapes a "live results" page for team names and caches results in the `team_cache` table (`TeamRepository`), keyed by year.
- `app/repositories/*.py` — SQLAlchemy async queries only (no business logic). Uses `select(...)`, `.overlap(...)` for Postgres array-column filters (`groups`, `disciplines`, `rank`).
- `app/models/*.py` — SQLAlchemy ORM models (`Event`, `TeamCache`), declarative base defined in `app/models/__init__.py`.
- `app/schemas/*.py` — Pydantic request/response models, separate from ORM models.
- `app/utils/parsers.py` / `app/utils/utils.py` — HTML scraping (BeautifulSoup) and Russian-language date-range parsing (`parse_date_range`, e.g. `"04 - 07 марта"` + year → `(start, end)` ISO dates). This is the trickiest part of the codebase and has the most direct test coverage in `app/tests/parser_test.py`.

### Database

- No Alembic migrations actually exist despite the dependency being installed and the README describing an `app/db/migrations/` folder — schema is created ad hoc via raw `CREATE TABLE IF NOT EXISTS` SQL in `startup_event()` (`app/core/db/database.py`), run on FastAPI startup. If you change a model's columns, update that SQL too, or the running DB won't match the ORM model.
- Two DB session factories exist and are both wired up: `app/core/db/database.py` (`get_db`) and `app/core/db/session.py` (`get_session`, used by the actual endpoints/deps). They point at the same engine/`AsyncSessionLocal`.
- Postgres only (asyncpg driver); `DATABASE_URL` is required (raises at import time if unset). `postgres://`/`postgresql://` URLs and a trailing `?sslmode=require`/`&sslmode=require` are auto-rewritten for asyncpg compatibility.

### Auth

`PermissionChecker`/`PermissionCheck` (`app/core/permissions.py`) is a no-op stub — it accepts any bearer token and always returns `True`. Don't assume it enforces anything; it's only wired into the root `/` and `/health` endpoints currently, not the events/teams routers.

### Config

All settings are in `app/core/config.py` (`Settings`, loaded from `.env`), including filter defaults for the external scrape (`EVENT_NAME`, `EVENT_YEAR`, `EVENT_GROUP`) and the external source URLs (`BASE_URL`, `LIVE_RESULTS_BASE_URL`).

## Language

This repo's `.kilocode/rules-code/rules.md` (rules for AI coding agents) states: always respond in Russian.

## Notes

- Filter vocab (ranks/types/groups/disciplines accepted by the external site and by `/api/v1/events`) is documented in README.md — check there before adding new filter values.
- Response bodies for `/events` and `/teams` endpoints are heavy with `print()`-based debug logging in the service/repository layers; this is intentional existing behavior for tracing scrape issues in production, not leftover debug code to be cleaned up incidentally.
