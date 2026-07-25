set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACMR)
FAILED=0

BACKEND_PY_FILES=$(echo "$STAGED_FILES" | grep -E '^apps/backend/.*\.py$' || true)
FRONTEND_FILES=$(echo "$STAGED_FILES" | grep -E '^apps/frontend/.*\.(vue|ts|tsx|js|jsx|cjs|mjs)$' || true)

# ── Backend: ruff + mypy ───────────────────────────────────────────────────
if [ -n "$BACKEND_PY_FILES" ]; then
  echo "-- Backend: ruff + mypy on staged files --"
  BACKEND_VENV="apps/backend/api-backend-env/bin"

  # Auto-fix what's fixable, then re-stage so the fix is part of this commit.
  echo "$BACKEND_PY_FILES" | xargs "$BACKEND_VENV/ruff" check --fix --config apps/backend/pyproject.toml --quiet
  echo "$BACKEND_PY_FILES" | xargs "$BACKEND_VENV/ruff" format --config apps/backend/pyproject.toml --quiet
  echo "$BACKEND_PY_FILES" | xargs git add

  if ! echo "$BACKEND_PY_FILES" | xargs "$BACKEND_VENV/ruff" check --config apps/backend/pyproject.toml; then
    echo "ruff: unresolved issues in staged files (see above)."
    FAILED=1
  fi

  # mypy needs the whole project graph to resolve imports correctly, so it
  # always checks all of src/ — but we only fail the commit on errors whose
  # file is actually staged.
  MYPY_OUTPUT=$(cd apps/backend && api-backend-env/bin/mypy --config-file pyproject.toml src 2>&1)
  MYPY_STAGED_ERRORS=""
  while IFS= read -r f; do
    [ -z "$f" ] && continue
    rel="${f#apps/backend/}"
    match=$(echo "$MYPY_OUTPUT" | grep -F "$rel:" || true)
    [ -n "$match" ] && MYPY_STAGED_ERRORS="${MYPY_STAGED_ERRORS}${match}
"
  done <<< "$BACKEND_PY_FILES"

  if [ -n "$MYPY_STAGED_ERRORS" ]; then
    echo "mypy: unresolved issues in staged files:"
    echo "$MYPY_STAGED_ERRORS"
    FAILED=1
  fi
fi

# ── Frontend: eslint + vue-tsc ───────────────────────────────────────────────
if [ -n "$FRONTEND_FILES" ]; then
  echo "-- Frontend: eslint + vue-tsc on staged files --"
  RELATIVE_FRONTEND_FILES=$(echo "$FRONTEND_FILES" | sed 's|^apps/frontend/||')

  (cd apps/frontend && echo "$RELATIVE_FRONTEND_FILES" | xargs npx eslint --fix --ignore-path .gitignore) || true
  (cd apps/frontend && echo "$RELATIVE_FRONTEND_FILES" | xargs npx prettier --write) || true
  echo "$FRONTEND_FILES" | xargs git add

  if ! (cd apps/frontend && echo "$RELATIVE_FRONTEND_FILES" | xargs npx eslint --ignore-path .gitignore); then
    echo "eslint: unresolved issues in staged files (see above)."
    FAILED=1
  fi

  # vue-tsc type-checks the whole project graph — only fail on errors whose
  # file is actually staged.
  TSC_OUTPUT=$(cd apps/frontend && npx vue-tsc --noEmit 2>&1)
  TSC_STAGED_ERRORS=""
  while IFS= read -r f; do
    [ -z "$f" ] && continue
    rel="${f#apps/frontend/}"
    match=$(echo "$TSC_OUTPUT" | grep -F "$rel(" || true)
    [ -n "$match" ] && TSC_STAGED_ERRORS="${TSC_STAGED_ERRORS}${match}
"
  done <<< "$FRONTEND_FILES"

  if [ -n "$TSC_STAGED_ERRORS" ]; then
    echo "vue-tsc: unresolved issues in staged files:"
    echo "$TSC_STAGED_ERRORS"
    FAILED=1
  fi
fi

if [ "$FAILED" -ne 0 ]; then
  echo
  echo "Pre-commit checks failed. Fix the issues above and try again."
  exit 1
fi

exit 0
