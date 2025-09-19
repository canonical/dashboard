# Variables
VENV := .venv
PYTHON := python3
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest
MANAGE := $(VENV)/bin/python ./manage.py

.PHONY: all help clean venv install install-dev migrate init test test-framework test-browser run collectstatic collectstatic-check

help:
	@echo "Available targets:"
	@echo "  install        - Create virtualenv and install dependencies"
	@echo "  migrate        - Setup database tables"
	@echo "  init           - Load initial test data"
	@echo "  run            - Start development server"
	@echo "  test           - Run automated tests"
	@echo "  collectstatic  - Copy static files to staticfiles directory"
	@echo "  clean          - Remove virtualenv and cache files"

venv:
	$(PYTHON) -m venv $(VENV)

install: venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

install-dev: install
	$(PIP) install -r requirements-dev.txt

migrate: install
	$(MANAGE) migrate

init: migrate
	$(MANAGE) loaddata initial_data.yaml

run: init
	$(MANAGE) runserver

collectstatic: install
	$(MANAGE) collectstatic --no-input

# For use in CI
collectstatic-check: collectstatic
	@if ! git diff --exit-code --quiet staticfiles/; then \
		echo "Modified static files detected. Please run 'make collectstatic' and commit the changes."; \
		exit 1; \
	fi

test: test-framework test-browser

# For use in CI
test-framework: install-dev
	$(PYTEST) framework

# For use in CI
test-browser: install-dev
	$(VENV)/bin/python -m playwright install
	$(PYTEST) test_browser.py

clean:
	rm -rf $(VENV)
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
