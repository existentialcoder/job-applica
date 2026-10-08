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
scripts/pre-commit.sh  husky pre-commit hook (runs `make check`)
Makefile               root-level check/fix targets (see below)
```

## Root-level tooling

- `Makefile` (repo root): `make check` / `make check-backend` / `make check-frontend` (read-only, CI-style) and `make fix` / `make fix-backend` / `make fix-frontend` (autofix). The Makefile is the single source of truth for lint/type rules.
- `scripts/pre-commit.sh` (husky pre-commit hook): just runs `make check` across the whole repo, whatever is staged — if `make fix` then `make check` pass, the commit passes. Add or change checks in the Makefile, never in the hook.
- Don't add `prettier --write` back into either the Makefile or the pre-commit script — see the frontend `CLAUDE.md`'s "No Prettier" section for why.

## Versioning

- Backend, frontend and website are not versioned — they deploy continuously (`.github/workflows/deploy.yml`, manual dispatch) and a deploy is identified by its commit (`GET /health` returns `commit`). `apps/frontend`/`apps/website` keep `"version": "0.0.0"` only because yarn 1 ignores workspaces without one; never bump it.
- `apps/browser-extension` is the one versioned component (the stores require a strictly increasing version). release-please (`release-please-config.json`, `.release-please-manifest.json`, `.github/workflows/release-extension.yml`) keeps a release PR open on `main` built from conventional commits touching that path; merging it bumps `package.json` + `public/manifest.json`, tags `extension-vX.Y.Z` and publishes to Chrome + Firefox. Don't bump the extension version by hand.

## General conventions

- No comments explaining *what* code does; only for non-obvious *why* (a workaround, a hidden constraint, a subtle invariant).
- Don't add error handling / validation for states that can't actually occur given the surrounding guarantees (prefer `assert` + a type-narrowing comment over a defensive `if`/`raise` for those).
- Prefer fixing the actual config/type mismatch over loosening a type to make an error go away — several fixes made in this codebase (TypedDict for filter params, `-> dict` instead of a dynamic model alias, tsconfig `paths`) were about making the types honestly describe what the code already does, not suppressing the checker.
