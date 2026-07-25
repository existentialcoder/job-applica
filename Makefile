.PHONY: check check-backend check-frontend fix fix-backend fix-frontend

BACKEND_VENV := apps/backend/api-backend-env/bin

# Read-only — reports issues, changes nothing, exits non-zero if any are found.
check: check-backend check-frontend

check-backend:
	@echo "-- Backend: ruff + mypy (check only) --"
	$(BACKEND_VENV)/ruff check --config apps/backend/pyproject.toml apps/backend/src
	$(BACKEND_VENV)/ruff format --check --config apps/backend/pyproject.toml apps/backend/src
	$(BACKEND_VENV)/mypy --config-file apps/backend/pyproject.toml apps/backend/src

check-frontend:
	@echo "-- Frontend: eslint + vue-tsc (check only) --"
	cd apps/frontend && npx eslint . --ext .vue,.js,.jsx,.cjs,.mjs,.ts,.tsx,.cts,.mts --ignore-path .gitignore
	cd apps/frontend && npx vue-tsc --noEmit

fix: fix-backend fix-frontend

fix-backend:
	@echo "-- Backend: ruff check --fix + ruff format --"
	-$(BACKEND_VENV)/ruff check --fix --config apps/backend/pyproject.toml apps/backend/src
	$(BACKEND_VENV)/ruff format --config apps/backend/pyproject.toml apps/backend/src

fix-frontend:
	@echo "-- Frontend: eslint --fix + prettier --write --"
	-cd apps/frontend && npx eslint . --ext .vue,.js,.jsx,.cjs,.mjs,.ts,.tsx,.cts,.mts --fix --ignore-path .gitignore
	cd apps/frontend && npx prettier --write src/
