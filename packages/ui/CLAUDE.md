# `@job-applica/ui` (`packages/ui`)

Shared shadcn-vue-style component library, consumed by `apps/frontend` (and any other workspace app that needs the same primitives) via the `@/components/ui/*` and `@job-applica/ui/*` aliases.

- Components live under `src/components/ui/<name>/` (radix-vue-based primitives: button, select, dialog, dropdown-menu, pagination, data-table, etc.) — see `package.json`'s `exports` map for what's importable (`.`, `./components/*`, `./lib/*`, `./theme`).
- Peer dependencies (`vue`, `radix-vue`, `class-variance-authority`, `clsx`, `tailwind-merge`, `lucide-vue-next`) are declared here but must actually be installed by the consuming app — this package doesn't bundle them.
- Adding a new primitive here makes it available to every consuming app automatically via the shared alias; don't duplicate a component locally in `apps/frontend/src/components/ui` — that directory doesn't exist and shouldn't be recreated (see `apps/frontend/CLAUDE.md`).
- When a consuming app adds an import path here (e.g. a new subfolder), double-check that app's `tsconfig` `paths`/`include` picks it up — see the "Path aliases" note in `apps/frontend/CLAUDE.md`; the bundler alias and the TypeScript alias are configured independently and can silently drift out of sync.
