.PHONY: help test lint format

help:
	@echo "Available targets:"
	@echo "  test    - Run pytest on the tests/ directory"
	@echo "  lint    - Run ruff linter"
	@echo "  format  - Run ruff formatter"

test:
	.venv/Scripts/python.exe -m pytest tests/

lint:
	.venv/Scripts/python.exe -m ruff check .

format:
	.venv/Scripts/python.exe -m ruff format .
