.PHONY: test lint format

test:
	.venv/Scripts/python.exe -m pytest tests/

lint:
	.venv/Scripts/python.exe -m ruff check .

format:
	.venv/Scripts/python.exe -m ruff format .
