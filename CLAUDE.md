# job-applica

Job applications tracking app. Monorepo (yarn workspaces) with a FastAPI backend, a Vue 3 frontend, a browser extension, and a marketing site, plus a shared UI component package.

Stack-specific conventions live in nested `CLAUDE.md` files — read the one for whatever you're touching:

- [`apps/backend/CLAUDE.md`](apps/backend/CLAUDE.md) — Python/FastAPI/SQLAlchemy/Alembic conventions.
- [`apps/frontend/CLAUDE.md`](apps/frontend/CLAUDE.md) — Vue/TypeScript/ESLint conventions, pagination patterns.
- [`packages/ui/CLAUDE.md`](packages/ui/CLAUDE.md) — shared component library.

This file covers only what's genuinely cross-cutting.

## Repo layout

```
apps/
  backend/            FastAPI + SQLAlchemy (async) + Pydantic v2 + Alembic
  frontend/           Vue 3 + Vite + TypeScript (main web app)
  browser-extension/  Vue 3 extension (Chrome Web Store — independently versioned)
  website/            Nuxt marketing site
packages/
  ui/                 @job-applica/ui — shared shadcn-vue-style component library
scripts/pre-commit.sh  husky pre-commit hook (backend + frontend checks)
Makefile               root-level check/fix targets (see below)
```

## Root-level tooling

- `Makefile` (repo root): `make check` / `make check-backend` / `make check-frontend` (read-only, CI-style) and `make fix` / `make fix-backend` / `make fix-frontend` (autofix). These should always mirror what `scripts/pre-commit.sh` does — if you change one, check the other.
- `scripts/pre-commit.sh` (husky pre-commit hook): runs ruff+mypy on staged backend `.py` files, eslint on staged frontend files. mypy and `vue-tsc` type-check the *whole* project graph (they need full context to resolve imports) but only fail the commit on errors whose file is actually staged — a slow pre-commit isn't necessarily about how much you personally changed.
- Don't add `prettier --write` back into either the Makefile or the pre-commit script — see the frontend `CLAUDE.md`'s "No Prettier" section for why.

## Versioning

- `apps/frontend`, `apps/backend`, and the root `package.json` version fields are currently unused (nothing reads them) — they're not the versioning mechanism for this repo, deploys are continuous.
- `apps/browser-extension` is the one component genuinely versioned (`yarn release:extension` / `:minor` / `:major`), because the Chrome Web Store requires a strictly incrementing manifest version on every submission. Keep it independent of everything else's release cadence.
- If real cross-app versioning is ever wanted, the root `package.json`'s version field is the natural single source of truth (ask before assuming this has been implemented — it hasn't, as of this writing).

## General conventions

- No comments explaining *what* code does; only for non-obvious *why* (a workaround, a hidden constraint, a subtle invariant).
- Don't add error handling / validation for states that can't actually occur given the surrounding guarantees (prefer `assert` + a type-narrowing comment over a defensive `if`/`raise` for those).
- Prefer fixing the actual config/type mismatch over loosening a type to make an error go away — several fixes made in this codebase (TypedDict for filter params, `-> dict` instead of a dynamic model alias, tsconfig `paths`) were about making the types honestly describe what the code already does, not suppressing the checker.
