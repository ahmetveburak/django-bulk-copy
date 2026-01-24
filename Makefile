.PHONY: help install db-up db-down migrate test lint type-check security check clean

DJANGO_SETTINGS_MODULE ?= tests.settings

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	uv sync --all-extras

db-up:  ## Start PostgreSQL container
	docker compose up -d
	@echo "Waiting for PostgreSQL to be ready..."
	@sleep 2

db-down:  ## Stop PostgreSQL container
	docker compose down -v

migrate:  ## Run Django migrations
	DJANGO_SETTINGS_MODULE=$(DJANGO_SETTINGS_MODULE) uv run python manage.py migrate

test: db-up migrate  ## Run tests with coverage
	DJANGO_SETTINGS_MODULE=$(DJANGO_SETTINGS_MODULE) uv run pytest tests/ --cov=bulk_copy --cov-report=term-missing

test-fast:  ## Run tests without coverage (faster)
	DJANGO_SETTINGS_MODULE=$(DJANGO_SETTINGS_MODULE) uv run pytest tests/ -x

lint:  ## Run Ruff linter
	uv run ruff check bulk_copy tests

lint-fix:  ## Run Ruff linter with auto-fix
	uv run ruff check --fix bulk_copy tests

type-check:  ## Run mypy type checker
	uv run mypy bulk_copy

security:  ## Run Bandit security scanner
	uv run bandit -c pyproject.toml -r bulk_copy

check: lint type-check security  ## Run all checks (lint + type + security)

ci: db-up migrate check test  ## Run full CI pipeline locally

clean:  ## Clean up containers and cache
	docker compose down -v
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
