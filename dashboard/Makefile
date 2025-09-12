# Variables
VENV := .venv
PYTHON := python3
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest
MANAGE := $(VENV)/bin/python ./manage.py

.PHONY: all help clean venv install migrate init test run

help:
	@echo "Available targets:"
	@echo "  install    - Create virtualenv and install dependencies"
	@echo "  migrate    - Setup database tables"
	@echo "  init       - Load initial test data"
	@echo "  run        - Start development server"
	@echo "  test       - Run automated tests"
	@echo "  clean      - Remove virtualenv and cache files"

venv:
	$(PYTHON) -m venv $(VENV)

install: venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

migrate: install
	$(MANAGE) migrate

init: migrate
	$(MANAGE) loaddata initial_data.yaml

run: init
	$(MANAGE) runserver

test: install
	$(PIP) install -r requirements-dev.txt
	$(VENV)/bin/python -m playwright install
	$(PYTEST)

clean:
	rm -rf $(VENV)
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete