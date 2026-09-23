SHELL := /bin/bash

.PHONY: install install-dev up down bootstrap test lint format-check format parity dvc-track dvc-push dvc-pull drift

install:
	python -m pip install -r requirements/runtime.txt -r requirements/training.txt

install-dev:
	python -m pip install -r requirements/runtime.txt -r requirements/training.txt -r requirements/dev.txt

up:
	docker compose up --build

down:
	docker compose down

bootstrap:
	docker compose run --rm bootstrap

test:
	python -m pytest

lint:
	python -m ruff check .

format-check:
	python -m ruff format --check .

format:
	python -m ruff format .
	python -m ruff check --fix .

parity:
	docker compose run --rm trainer python scripts/parity_check.py

drift:
	docker compose run --rm trainer python scripts/check_drift.py

dvc-track:
	docker compose run --rm trainer dvc add data/raw artifacts
	git add data/raw.dvc artifacts.dvc .gitignore

dvc-push:
	docker compose run --rm trainer dvc push

dvc-pull:
	docker compose run --rm trainer dvc pull
