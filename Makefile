# Makefile for the Morvo AI Marketing Platform

.PHONY: help test lint format deadcode requirements fix-imports fix-all check-errors

# Define the default shell
SHELL := /bin/bash

# Get the Python interpreter from the virtual environment
PYTHON := poetry run python

help:
	@echo "Commands:"
	@echo "  make test          - Run all tests with pytest"
	@echo "  make lint          - Run linters (ruff, mypy)"
	@echo "  make format        - Format code with black and isort"
	@echo "  make deadcode      - Find dead code with vulture"
	@echo "  make requirements  - Export dependencies to requirements.txt"
	@echo "  make fix-imports   - Remove unused imports and variables"
	@echo "  make fix-all       - Auto-fix all possible issues"
	@echo "  make check-errors  - Check for runtime errors with error tracking"

test:
	@echo "Running tests..."
	$(PYTHON) -m pytest

lint:
	@echo "Running linters..."
	poetry run ruff check app
	poetry run mypy app

format:
	@echo "Formatting code..."
	poetry run black app
	poetry run isort app

deadcode:
	@echo "Finding dead code with Vulture..."
	poetry run vulture app --min-confidence 80

requirements:
	@echo "Exporting dependencies to requirements.txt..."
	poetry export -f requirements.txt --output requirements.txt --without-hashes

fix-imports:
	@echo "Removing unused imports and variables..."
	poetry run autoflake --remove-all-unused-imports --remove-unused-variables --in-place --recursive app

fix-all:
	@echo "Auto-fixing all possible issues..."
	poetry run autoflake --remove-all-unused-imports --remove-unused-variables --in-place --recursive app
	poetry run black app
	poetry run isort app
	poetry run ruff check app --fix
	@echo "✅ All auto-fixes applied!"

check-errors:
	@echo "Checking for potential runtime errors..."
	$(PYTHON) -c "from app.core.error_tracking_example import *; print('✅ Error tracking examples work!')"
	@echo "💡 Add SENTRY_DSN to your .env file to enable error tracking"
