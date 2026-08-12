# Backend (`apps/backend`)

Python 3.12+, FastAPI, SQLAlchemy 2.x async ORM, Pydantic v2, Alembic for migrations. See the root [`CLAUDE.md`](../../CLAUDE.md) for repo-wide conventions.

## Virtualenv — exactly one, always

`apps/backend/api-backend-env` is the only venv that should ever exist. Never hand-create a second one (e.g. `api-backend-venv`); if lint tooling seems missing from the venv, fix `make build` / reinstall into the canonical one rather than creating a new one. `make build` installs **both** `requirements.txt` and `requirements-dev.txt` (the dev file carries `ruff`/`mypy`) — if a fresh venv is missing those tools, that's the target to check first.

Run the backend locally: `make run-local` (starts Postgres in Docker, builds the venv, runs migrations, starts uvicorn with `--reload`).

## Linting & typing

- Ruff config lives in `apps/backend/pyproject.toml`: `select = ["E", "F", "I", "UP"]`, line-length 120. `E712` (`== True`/`== False`) is deliberately ignored — SQLAlchemy filter expressions like `Model.col == True` need the literal comparison; ruff's autofix would silently break the query.
- The `I` selector is ruff's isort equivalent — it already enforces import order (stdlib → third-party → first-party/local, alphabetized within each group; relative imports (`from ..x import y`) auto-classify as local-folder). Run `ruff check --select I --fix` if imports drift.
- mypy config is also in `pyproject.toml` (`check_untyped_defs`, `warn_unused_ignores`, `ignore_missing_imports`). Run via `apps/backend/api-backend-env/bin/mypy --config-file pyproject.toml src`.
- `make check` / `make check-backend` (read-only) and `make fix` / `make fix-backend` (autofix) run these from the repo root.

## Typing patterns established in this codebase

- A dict-shaped "filter params" object that gets subscripted (`filter['name']`) should be a `TypedDict`, not a plain class — plain classes don't support `__getitem__` and will both fail mypy and fail at runtime.
- Don't annotate a function's return type with a *value* produced by a factory function (e.g. `PaginatedJobs = get_paginated_response_model(JobBase)` used as `-> PaginatedJobs`) unless the function actually returns an instance of that type. Those dynamic pydantic models are only valid as FastAPI's `response_model=` argument (a runtime value), not as a Python type annotation. If the function actually returns a plain `dict`, annotate `-> dict`.
- SQLAlchemy's `.scalar()` on a nullable-returning query is typed `T | None` — guard with `or 0` (counts) before passing into a strictly-`int`-typed parameter, rather than loosening the parameter's type.
- When a field is `Optional` at the schema level only because the schema is shared across create/read contexts (e.g. `BaseSchema.id: int | None`), but a given code path only ever runs with it populated (e.g. an authenticated user), narrow with `assert x is not None` rather than adding real error-handling for a case that can't happen.
- Match a function's parameter/return types to how it's *actually called* — if callers always pass a dict literal or `None`, the signature should say so, not the other way around.

## Migrations (Alembic)

- Single linear history, one head — check `alembic heads` returns exactly one revision before considering a migration branch resolved.
- Data-shape changes to existing rows (e.g. adding a new mandatory key to a JSONB array column) need a real backfill migration — don't just change application-level validation/defaults and assume existing rows already match.
- Keep `server_default` in the migration's `op.add_column`/`op.alter_column` in sync with the SQLAlchemy model's `mapped_column(..., server_default=...)` — they drift independently and only one of them actually affects the DB.
- Before a migration that transforms/moves data (e.g. denormalizing a FK relationship into JSONB), sanity-check for orphaned references that would silently become `NULL`/dropped data.

## Job filtering & pagination

- `GET /jobs` (`api/v1/routes/jobs.py`) already supports simultaneous `status` + `board_id` + `page`/`per_page` filtering — `JobFilterParams.status`/`.board_id` are `list[str]`, and `parse_field_as_required` (`schemas/job.py`) splits a single comma-free string into a one-item list, so a single-status query works the same way as a multi-status one. No backend changes were needed to support the frontend's per-kanban-column pagination (see the frontend `CLAUDE.md`).
- `build_paginated_response` (`api/deps/pagination.py`) returns `{meta: {total, page, per_page, total_pages, has_next, has_prev}, results}` — a plain `dict`, not a pydantic model instance (see the `PaginatedJobs` typing note above).
- User preferences are stored in `users.settings` (JSONB). `PATCH /users/{id}/settings` (`services/user.py`) does a **shallow merge** (`{**old, **patch}`), not an overwrite — adding a new preference key needs no backend change, just a new key in the PATCH payload from the frontend.
