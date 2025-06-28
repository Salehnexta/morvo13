# Morvo Makefile

.PHONY: help dev lint tests coverage docker-up docker-down gradio

help:
	@echo "Usage: make <target>"
	@echo "Available targets:"
	@echo "  dev           Start FastAPI + Celery in uvicorn reload mode"
	@echo "  lint          Run ruff, black --check, isort --check, mypy"
	@echo "  tests         Run pytest with coverage"
	@echo "  coverage      Generate HTML coverage report"
	@echo "  docker-up     docker compose up -d --build"
	@echo "  docker-down   docker compose down -v"
	@echo "  gradio        Launch temporary Gradio UI"

install:
	poetry install --no-interaction --with dev,prod

lint:
	poetry run ruff check . && \
	poetry run black --check . && \
	poetry run isort --check . && \
	poetry run mypy .

tests:
	poetry run pytest -q --cov=app --cov-report=term-missing --cov-fail-under=80

coverage:
	poetry run pytest --cov=app --cov-report=html && open htmlcov/index.html

dev:
	poetry run uvicorn app.main:app --reload

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down -v

# ---- Front-end helpers ----
# Launch temporary Gradio UI (frontend/gradio_ui.py)
gradio:
	poetry run python -m frontend.gradio_ui
