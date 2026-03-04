.DEFAULT_GOAL := all
LOG_LEVEL = INFO

.PHONY: all
all: ## Show the available make targets.
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@fgrep "##" Makefile | fgrep -v fgrep

.PHONY: clean
clean: ## Clean the temporary files.
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .coverage
	rm -rf .ruff_cache
	rm -rf megalinter-reports

.PHONY: format
format:  ## Format the code.
	poetry run black .
	poetry run ruff check . --fix

.PHONY: lint
lint:  ## Run all linters (black/ruff/pylint/mypy).
	poetry run black --check .
	poetry run ruff check .
	poetry run pylint -j 0 eq_cir_management_ui tests --reports=n --output-format=colorized
	make mypy

.PHONY: run
run:  ## Run flask on port 5100.
	poetry run flask --app app run --port 5100

.PHONY: gunicorn
gunicorn:  ## Run the app with Gunicorn.
	poetry run gunicorn --bind 0.0.0.0:5100 app:app

.PHONY: test
test:  ## Run the tests and check coverage.
	poetry run pytest -n auto --cov=eq_cir_management_ui --cov-report term-missing --cov-fail-under=100

.PHONY: mypy
mypy:  ## Run mypy.
	poetry run mypy eq_cir_management_ui

.PHONY: install
install:  ## Install the dependencies excluding dev.
	poetry install --only main

.PHONY: install-dev
install-dev:  ## Install the dependencies including dev.
	poetry install

.PHONY: megalint
megalint:  ## Run the mega-linter.
	docker run --platform linux/amd64 --rm \
		-v /var/run/docker.sock:/var/run/docker.sock:rw \
		-v $(shell pwd):/tmp/lint:rw \
		ghcr.io/oxsecurity/megalinter-python:v9.4.0
