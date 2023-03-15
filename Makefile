#* Variables
SHELL := /usr/bin/env bash
PYTHON := python
PYTHONPATH := `pwd`

#* Installation and Updates
.PHONY: install
install:
	pipx install pdm
	pipx inject pdm pdm-multirun
	pdm install --no-self
	pdm run pre-commit install
	pdm run mypy --install-types --non-interactive --config-file pyproject.toml ./

.PHONY: update
update:
	pdm update

.PHONY: update-dev-deps
update-dev-deps:
	pdm update -d --no-self

#* Formatters
.PHONY: format
format:
	pdm run autoflake -ir --exclude tests/fixtures --remove-all-unused-imports ./
	pdm run pyupgrade --exit-zero-even-if-changed --py39-plus
	pdm run isort --settings-path pyproject.toml ./
	pdm run black --config pyproject.toml ./
	pdm run eof ./
	pdm run ruff check . --fix

#* Testing
.PHONY: unit-test
unit-test:
	PYTHONPATH=$(PYTHONPATH)/src pdm run pytest -c pyproject.toml --cov-report=html --cov=src tests/unit/

.PHONY: integration-test
integration-test:
	PYTHONPATH=$(PYTHONPATH)/src pdm run pytest -c pyproject.toml --cov-report=html --cov=src tests/integration

.PHONY: all-test
all-test:
	PYTHONPATH=$(PYTHONPATH)/src pdm run pytest -c pyproject.toml --cov-report=html --cov=src tests/

.PHONY: check-style
check-style:
	pdm run isort --diff --check-only --settings-path pyproject.toml ./
	pdm run black --diff --check --config pyproject.toml ./
	pdm run ruff check .

.PHONY: mypy
mypy:
	pdm run mypy --config-file pyproject.toml ./

.PHONY: check-security
check-security:
	pdm run bandit -ll --recursive src tests

.PHONY: check-all
check-all: check-style mypy check-security all-test

#* Cleaning
.PHONY: pycache-remove
pycache-remove:
	find . | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf

.PHONY: mypycache-remove
mypycache-remove:
	find . | grep -E ".mypy_cache" | xargs rm -rf

.PHONY: ipynbcheckpoints-remove
ipynbcheckpoints-remove:
	find . | grep -E ".ipynb_checkpoints" | xargs rm -rf

.PHONY: pytestcache-remove
pytestcache-remove:
	find . | grep -E ".pytest_cache" | xargs rm -rf

.PHONY: build-remove
build-remove:
	rm -rf build/

.PHONY: cleanup
cleanup: pycache-remove mypycache-remove ipynbcheckpoints-remove pytestcache-remove
