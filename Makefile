.PHONY: help test lint format

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

test:
	$(PYTHON) -m pytest tests/

lint:
	$(PYTHON) -m ruff check .

format:
	$(PYTHON) -m ruff format .
