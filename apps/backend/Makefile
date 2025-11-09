SHELL := /bin/bash
.ONESHELL:
.PHONY: build run-local activate-env

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

run-local: build
	@echo "🔹 Running the project locally..."
	chmod +x ./run.sh
	$(VENV_DIR)/bin/python -m uvicorn src.main:app --reload

