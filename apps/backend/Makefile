SHELL := /bin/bash
.PHONY: build services dev

VENV_DIR := api-backend-env
COMPOSE  := docker compose -f ../../docker/docker-compose.yml

build: $(VENV_DIR)/.installed
$(VENV_DIR)/.installed: requirements.txt requirements-dev.txt
	test -d $(VENV_DIR) || python3 -m venv $(VENV_DIR)
	$(VENV_DIR)/bin/pip install -r requirements.txt -r requirements-dev.txt
	touch $@

services:
	$(COMPOSE) up -d --wait
	@echo "📬 Caught emails: http://localhost:8025"

dev: services build
	$(VENV_DIR)/bin/alembic upgrade head
	$(VENV_DIR)/bin/python -m uvicorn src.main:app --reload
