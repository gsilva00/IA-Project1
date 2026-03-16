.PHONY: run ruff lint format

run:
	uv run woodblock

ruff: lint format

lint:
	uv run ruff check --fix .

format:
	uv run ruff format .

typecheck:
	uv run mypy .
