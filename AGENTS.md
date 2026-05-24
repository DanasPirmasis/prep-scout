# Repository Guidelines

## Project Structure & Module Organization

This Python 3.13 project is managed with `uv`. Application code lives in `src/`: `src/models/` defines SQLModel tables, `src/queries/` contains database helpers, and `src/scraper/` contains scraping clients, runner code, and LastMile logic. Tests live in `tests/`, with JSON fixtures under `tests/fixtures/responses/` and expected outputs under `tests/fixtures/expected/`. Alembic setup is in `migrations/`, with generated revisions in `migrations/versions/`.

## Build, Test, and Development Commands

- `uv sync`: install project and development dependencies from `pyproject.toml` and `uv.lock`.
- `make test`: run the full pytest suite.
- `make lint`: run Ruff lint checks across the repository.
- `make lint-fix`: apply Ruff's safe automatic fixes.
- `make format`: format Python files with Ruff.
- `make format-check`: verify formatting without modifying files.
- `make typecheck`: run Pyright against `src/`.
- `make q`: run the local quality pass.

Use `docker-compose.yml` for local infrastructure. Keep schema changes in Alembic migrations.

## Coding Style & Naming Conventions

Follow Ruff formatting with a 120-character line length and Python 3.13 syntax. Ruff checks include `E`, `F`, import sorting, bugbear, pyupgrade, and simplify rules. Use explicit type hints for public functions and data boundaries. Name tests and functions in snake_case, classes in PascalCase, and constants in UPPER_SNAKE_CASE. Keep source-specific scraper code under `src/scraper/<source>/`.

## Testing Guidelines

Tests use `pytest`. Name test files `test_*.py` and test functions `test_<behavior>`. Prefer fixtures for external API payloads instead of live network calls. Current LastMile tests validate parsing, category tree construction, and save orchestration. Run `make test` before submitting changes. Add focused tests when changing models, queries, scraper parsing, or persistence behavior.

## Agent-Specific Instructions

Agents may edit files and run checks, but must not create commits under any circumstances. Leave changes unstaged unless the user explicitly asks for staging. After code generation or code edits, run `make q` and report modified files and verification results.

## Security & Configuration Tips

Do not commit credentials, API keys, database URLs, or private payloads. Use environment variables or local `.env` files for secrets, and keep fixture data sanitized. Avoid tests that require live Oxylabs or database access unless clearly marked.
