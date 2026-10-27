# Frontend (`apps/frontend`)

Vue 3 `<script setup lang="ts">`, Composition API, Pinia stores, Vite, Vue Router. See the root [`CLAUDE.md`](../../CLAUDE.md) for repo-wide conventions.

- Keep the TypeScript pin in `package.json` at or above whatever the installed Vue version's `.d.ts` files require (e.g. Vue's types use `NoInfer`, which needs TS 5.4+).

## Data flow — views → stores → dataservice

Views and components always go through Pinia stores (`src/stores/`). If no store covers the data yet, add one (or an action to an existing one) instead of calling the API from the component. Call `@/lib/dataservice` directly from a component only when a store genuinely adds nothing: a one-off call whose result no other component reads and that has no cached or shared state.

## No Prettier — ESLint owns all formatting

Prettier was removed deliberately; don't reintroduce it (or `@vue/eslint-config-prettier`) without a deliberate decision. `.eslintrc.cjs` enforces formatting directly:

- `semi: always`, `quotes: single`, `comma-dangle: never`, `indent: 2` (`SwitchCase: 1`)
- `brace-style: 1tbs`, no single-line blocks — applies to every block, not just `if`
- `import/order`: `builtin → external → internal (@/**) → parent → sibling → index`, alphabetized case-insensitively, no blank lines between groups

ESLint can't reflow long lines (no `printWidth` equivalent) — wrap them by hand. Apply everything else with `make fix-frontend`.

## Path aliases — defined in two places

- `@/*` → `apps/frontend/src/*`
- `@/components/ui/*` and `@job-applica/ui/*` → `packages/ui/src`

Every alias must exist in **both** `vite.config.ts` (`resolve.alias`) and the tsconfig `compilerOptions.paths` (plus a matching `include` glob). They drift independently: a bundler-only alias runs fine but fails type-checking with `TS2307`.

## `noEmit` / composite project references

`tsconfig.app.json` and `tsconfig.node.json` set `"noEmit": false` to override `@vue/tsconfig`'s default, which conflicts with `composite: true` + project references. Without it `vue-tsc` fails with `TS6310` and silently type-checks nothing — if its output looks suspiciously clean, check this override first.

## Design system — `packages/ui`

Every new UI feature follows the design system in `@job-applica/ui`:

- **Use what exists first.** Build screens from the existing components in `packages/ui/src/components/ui/` (button, card, dialog, sheet, form, input, select, multi-select, combobox, data-table, tabs, badge, tooltip, PageHeader, Skeleton, Loader, etc.) and the theme tokens in `packages/ui/src/theme`. Don't use raw colors or one-off styles where a token or variant exists.
- **If a component is missing, add it to `packages/ui`**, in the same shadcn-vue/radix-vue style as its neighbours, then use it from the app.
- **Never reinvent a component outside the package**: no hand-rolled buttons, modals, dropdowns, inputs and so on in `apps/*`, and no copied-and-tweaked versions of a package component. Extend the package component (a new variant or prop) instead. App-level components in `apps/frontend/src/components/` should compose package primitives, not replace them.
- There is no `apps/frontend/src/components/ui` — don't create one.
- Importable entry points are whatever `packages/ui/package.json`'s `exports` map lists.
- Its peer dependencies (`vue`, `radix-vue`, `class-variance-authority`, `clsx`, `tailwind-merge`, `lucide-vue-next`) aren't bundled — the consuming app must install them.
- A new import path into the package needs the tsconfig alias check above.

## User preferences

Per-user preferences live in the `users.settings` JSONB column and go through `useSettingsStore` (`stores/settings.ts`). To add one: add a typed field to `Settings`, its snake_case key to `WIRE_KEYS`, and a setter that calls `updateSettings`. The backend shallow-merges the patch, so new keys need no backend change.

## Lists and pagination

- Page-based lists use the shared `Pagination` component; the view owns `page`/`per_page` and loads through its store.
- Kanban-style boards paginate each column independently (infinite scroll, own `{ items, page, total, loading }` state per column). The board receives shared filters minus the column-scoping field and fetches per column, not a flat pre-filtered array.
- Mutations on a board (drag between columns, delete) update the affected columns' local state optimistically **and** emit up so the parent persists. Don't replace this with a full reload — it would reset every column's scroll position and page.
- Build filters in one function per view and derive every fetch from it; extend that function when adding a filter instead of building filters in a second place.
