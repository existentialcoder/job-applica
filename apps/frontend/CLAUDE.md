# Frontend (`apps/frontend`)

Vue 3 `<script setup lang="ts">`, Composition API, Pinia stores, Vite, Vue Router. See the root [`CLAUDE.md`](../../CLAUDE.md) for repo-wide conventions.

- TypeScript is pinned in `package.json` — currently `~5.4.0` (bumped from `~5.3.0` because Vue's `.d.ts` files use `NoInfer`, a TS 5.4+ utility type; keep the pin at least at whatever the installed Vue version's type defs require).

## No Prettier — ESLint owns all formatting

Prettier was deliberately removed from this project. `.eslintrc.cjs` no longer extends `@vue/eslint-config-prettier/skip-formatting`, and instead sets these rules directly:

- `semi: ['error', 'always']` — statements always end in `;`.
- `quotes: ['error', 'single']`
- `brace-style: ['error', '1tbs', { allowSingleLine: false }]` — opening brace stays on the same line as `if`/`function`/`for`/etc (K&R style); this applies uniformly to all blocks, ESLint has no way to scope it to `if` only.
- `indent: ['error', 2, { SwitchCase: 1 }]`
- `comma-dangle: ['error', 'never']`
- `import/order` (via `eslint-plugin-import`) — groups imports as `builtin → external → internal (@/**) → parent → sibling → index`, alphabetized case-insensitively within each group, no forced blank lines between groups.

Known gap from dropping Prettier: there's no auto-fixable line-wrapping equivalent to Prettier's `printWidth`. ESLint's `max-len` can only flag an overlong line, not reflow it — long lines get fixed by hand.

Run `eslint --fix` (via `npm run lint`, or `make fix-frontend` / `make fix` from root) to apply all of the above. `apps/frontend/.prettierrc.json` and the `prettier`/`@vue/eslint-config-prettier` deps are gone — don't reintroduce them without a deliberate decision to revisit this.

## Path aliases — must be defined in two places, not one

- `@/*` → `apps/frontend/src/*`
- `@/components/ui/*` and `@job-applica/ui/*` → the shared `packages/ui/src` workspace package.

Both the Vite bundler (`vite.config.ts`'s `resolve.alias`) **and** TypeScript (`tsconfig.app.json`/`tsconfig.json`'s `compilerOptions.paths`, plus the matching glob in `include`) need this mapping independently. The bundler alias existing alone means the app runs fine but TypeScript/the IDE can't resolve the import (`TS2307`) — this bit us when adding the pagination component and had gone unnoticed for every other `@/components/ui/*` import already in the codebase.

## `noEmit` / composite project references

`tsconfig.app.json` and `tsconfig.node.json` both explicitly set `"noEmit": false`. This overrides a default `"noEmit": true` baked into `@vue/tsconfig`'s base config, which conflicts with `composite: true` + project references (a known, documented upstream issue in `@vue/tsconfig`). Without this override, `vue-tsc --noEmit` fails immediately with `TS6310` on the referenced projects and **never actually type-checks anything** — silently. If `vue-tsc` output looks suspiciously empty/too-clean, verify this override is still in place before trusting a "no errors" result.

## Shared UI package (`packages/ui`)

All shadcn-vue-style primitives (button, select, dialog, dropdown-menu, pagination, etc.) live in `packages/ui/src/components/ui/*`, not locally under `apps/frontend/src/components/ui`. That local directory doesn't exist — don't recreate it; add new primitives to `packages/ui` instead. See [`packages/ui/CLAUDE.md`](../../packages/ui/CLAUDE.md).

## User settings persistence pattern

Arbitrary per-user preferences (view mode, page size, theme, etc.) are stored in the `users.settings` JSONB column and follow one consistent read/write pattern — mirror it for any new preference rather than inventing a new mechanism:

```ts
// read on mount
onMounted(async () => {
  const settings = await dataservice.getSettings();
  if (/* validate shape */) myRef.value = settings.my_key;
});

// write on change
watch(myRef, (val) => {
  dataservice.updateSettings({ my_key: val });
});
```

`dataservice.updateSettings()` PATCHes `/users/{id}/settings`, and the backend does a shallow merge into the JSONB column — no backend changes needed to add a new key. See `Applications.vue`'s `pageSize`/`selectedLayout` for two live examples.

## Pagination patterns

Two distinct pagination models exist in `Applications.vue` / `BoardApplications.vue` — don't conflate them when extending either:

**Table view (`TableApplications`)** — classic page-based pagination via the shared `Pagination` component (`@/components/ui/pagination`, wraps radix-vue's `PaginationRoot`). `Applications.vue` owns `currentPage`/`pageSize` refs and calls `dataservice.getJobs({ ...filters, page, per_page })` through `loadJobs()`. `pageSize` is persisted via the settings pattern above, with options `[10, 20, 50, 100]`.

**Board/kanban view (`BoardApplications`)** — each stage column paginates *independently* via infinite scroll, not a single shared page number:

- `BoardApplications` does **not** receive a flat `jobs` array. It receives a `base-filters` prop (all the shared filters *except* `status` — the filter panel's status multi-select has no effect in board view, since each column already scopes itself to exactly one status) and fetches its own data per column.
- Each column tracks `{ jobs, page, total, loading }` in a `reactive<Record<string, ColumnState>>`. On mount, every column independently loads page 1 at 10 items (`PAGE_SIZE` const in `BoardApplications.vue`).
- A `@scroll` handler on each column's card container fetches the next page when scrolled within `SCROLL_THRESHOLD_PX` of the bottom, gated on `!loading && hasMore`.
- Drag-and-drop status changes and deletes mutate the relevant column(s)' local arrays directly (optimistic UI) *in addition to* emitting the existing `status-change`/`delete` events up to `Applications.vue`, which still does the actual API persistence. Don't remove the local mutation and rely on a full reload — that was the previous (now-removed) `jobsByStatus` computed-from-flat-`jobs` model, and reintroducing it would break per-column independent pagination.
- Quick-add-card: `BoardApplications` exposes `refreshColumn(status)` via `defineExpose`; `Applications.vue` holds a template ref (`boardRef`) and calls it after the create API call succeeds, to pull in the new card without touching other columns.
- `Applications.vue`'s `buildBaseFilters()` is the single source of the shared filter-building logic — both `loadJobs()` (table) and the `boardBaseFilters` computed (board) derive from it. Extend that one function when adding a new filter field, rather than duplicating filter-construction logic in a second place.
