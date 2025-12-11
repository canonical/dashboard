# Variables
VENV := .venv
PYTHON := python3
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest
MANAGE := $(VENV)/bin/python ./manage.py

.PHONY: all help clean venv install install-dev migrate init test test-framework test-browser run collectstatic collectstatic-clear collectstatic-check makemigrations makemigrations-check

help:
	@echo "Available targets:"
	@echo "  install         - Create virtualenv and install dependencies"
	@echo "  migrate         - Setup database tables"
	@echo "  init            - Load initial test data"
	@echo "  run             - Start development server"
	@echo "  collectstatic   - Copy static files to staticfiles directory"
	@echo "  makemigrations  - Create new migrations based on model changes"
	@echo "  test            - Run automated tests"
	@echo "  clean           - Remove virtualenv and cache files"

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
collectstatic-clear: install
	$(MANAGE) collectstatic --clear --no-input

# For use in CI
collectstatic-check: collectstatic-clear
	@changes=$$(git status --porcelain staticfiles | wc -l); \
	if [ $$changes -gt 0 ]; then \
		echo "Detected changes to static files. Run 'make collectstatic-clear' and commit the changes."; \
		exit 1; \
	fi

makemigrations: install
	$(MANAGE) makemigrations --no-input

# For use in CI
makemigrations-check: makemigrations
	@changes=$$(git status --porcelain */migrations | wc -l); \
	if [ $$changes -gt 0 ]; then \
		echo "Detected changes to migrations. Run 'make makemigrations' and commit the changes."; \
		exit 1; \
	fi

test: test-framework test-projects test-browser

# For use in CI
test-framework: install-dev
	$(PYTEST) framework

# For use in CI
test-projects: install-dev
	$(PYTEST) projects

# For use in CI
test-browser: install-dev
	$(VENV)/bin/python -m playwright install
	$(PYTEST) test_browser.py

clean:
	rm -rf $(VENV)
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
