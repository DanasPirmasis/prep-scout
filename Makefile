.PHONY: lint format format-check typecheck q

lint:
	uv run ruff check .

format:
	uv run ruff check . --fix
	uv run ruff format .

format-check:
	uv run ruff format --check .

typecheck:
	uv run pyright

q: lint format-check typecheck
