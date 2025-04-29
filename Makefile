.PHONY: clean clean-test clean-pyc clean-build docs help lint test test-all coverage build dist install dev-install release
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

lint: ## check style with flake8 and isort
	flake8 wp_api tests
	isort --check-only --diff wp_api tests
	black --check wp_api tests

format: ## format code with black and isort
	isort wp_api tests
	black wp_api tests

test: ## run tests quickly with the default Python
	pytest

test-all: ## run tests on every Python version with tox
	tox

coverage: ## check code coverage quickly with the default Python
	pytest --cov=wp_api --cov-report=term-missing
	$(BROWSER) htmlcov/index.html

docs-deps: ## install documentation dependencies
	pip install -e ".[docs]"

docs: docs-deps ## generate Sphinx HTML documentation, including API docs
	mkdir -p docs/modules
	rm -f docs/wp_api.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ wp_api
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

build: clean ## build using modern build system
	python -m build

dist: clean ## builds source and wheel package (legacy)
	python -m build

release: dist ## package and upload a release
	twine upload dist/*

install: clean ## install the package to the active Python's site-packages
	pip install .

dev-install: clean ## install the package in development mode
	pip install -e ".[dev]"