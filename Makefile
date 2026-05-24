.PHONY: lint lint-fix format format-check typecheck test q

lint:
	uv run ruff check .

lint-fix:
	uv run ruff check --fix .

format:
	uv run ruff format .

format-check:
	uv run ruff format --check .

typecheck:
	uv run pyright

test:
	uv run pytest

q: lint-fix format lint typecheck
