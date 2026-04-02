.PHONY: help test lint format build publish ci

ifeq ($(OS),Windows_NT)
PYTHON = .venv/Scripts/python.exe
else
PYTHON = .venv/bin/python
endif

help:
	@echo "Available targets:"
	@echo "  test    - Run pytest on the tests/ directory"
	@echo "  lint    - Run ruff linter"
	@echo "  format  - Run ruff formatter"
	@echo "  build   - Clean and build dist packages"
	@echo "  publish - Build and upload to PyPI"
	@echo "  ci      - Run lint and tests"

test:
	$(PYTHON) -m pytest tests/

lint:
	$(PYTHON) -m ruff check .

format:
	$(PYTHON) -m ruff format .

build:
	rm -rf dist/ build/ hwidgen.egg-info/
	$(PYTHON) -m build --outdir dist/

publish: build
	$(PYTHON) -m twine upload dist/*

ci: lint test
