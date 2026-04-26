SHELL := /bin/bash
.ONESHELL:
.PHONY: build run-local run-db activate-env

DB_CONTAINER := some-postgres
DB_VOLUME    := postgres_data

VENV_DIR := api-backend-env
PYTHON := python3
PIP := $(VENV_DIR)/bin/pip

activate-env:
	@echo "🔹 Activating virtual environment..."
	if [ ! -d "$(VENV_DIR)" ]; then
		echo "Creating virtual environment..."
		$(PYTHON) -m venv $(VENV_DIR)
	fi
	source $(VENV_DIR)/bin/activate
	echo "✅ Virtual environment activated."

build: activate-env
	@echo "🔹 Installing dependencies..."
	$(PIP) install -r requirements.txt
	@echo "✅ Dependencies installed."

run-db:
	@echo "🔹 Starting PostgreSQL..."
	if docker ps -q -f name=$(DB_CONTAINER) | grep -q .; then \
		echo "✅ PostgreSQL already running."; \
	elif docker ps -aq -f name=$(DB_CONTAINER) | grep -q .; then \
		docker start $(DB_CONTAINER); \
		echo "✅ PostgreSQL container restarted."; \
	else \
		docker volume create $(DB_VOLUME); \
		docker run \
			--name $(DB_CONTAINER) \
			-e POSTGRES_PASSWORD=password \
			-p 5432:5432 \
			-v $(DB_VOLUME):/var/lib/postgresql/data \
			-d postgres; \
		echo "✅ PostgreSQL container created with persistent volume '$(DB_VOLUME)'."; \
	fi

run-local: run-db build
	@echo "🔹 Running the project locally..."
	chmod +x ./run.sh
	$(VENV_DIR)/bin/python -m uvicorn src.main:app --reload

