# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Rules

- Do NOT suggest adding `__init__.py` files. This project does not use them.

## Commands

```bash
# Start PostgreSQL
docker-compose up -d

# Run migrations
alembic upgrade head

# Generate a new migration
alembic revision --autogenerate -m "description"

# Run the scraper
uv run python -m src.main

# Install dependencies
uv sync

# Run tests
make test

# Lint / format / typecheck
make lint          # ruff check
make lint-fix      # ruff check --fix
make format        # ruff format
make format-check  # ruff format --check (CI mode)
make typecheck     # pyright against src/
make q             # lint-fix + format + lint + typecheck (full quality pass)
```

## Architecture

**prep-scout** is one service in a multi-service system. It scrapes grocery prices from three Lithuanian e-commerce stores (Barbora.lt, Rimi.lt, LastMile.lt), stores products in its own PostgreSQL database, and publishes events to Redis Streams for downstream services.

### Responsibilities

prep-scout is responsible for scraping and publishing only. Price history, cross-store matching, and user-facing features live in other services.

### Data flow

1. `src/main.py` — entry point; calls `run_scraper()` directly.
2. `src/scraper/runner.py` — initialises an Oxylabs `RealtimeClient` and dispatches to store-specific scrapers.
3. Scrapers read the existing product by `(store, external_id)`. If not found → insert and publish `product.created`. If found → update and publish `product.updated`.

### Events published

| Event             | Trigger                        | Consumers            |
| ----------------- | ------------------------------ | -------------------- |
| `product.created` | New product scraped first time | prep-link, prep      |
| `product.updated` | Known product scraped again    | prep                 |

Both events carry the full product payload: `store`, `external_id`, `name`, `brand`, `category`, `unit`, `comparative_unit`, `price`.

### Scraper design (see SCRAPER.md for full spec)

Each store delivers product data differently:

| Store       | Format                                                   |
| ----------- | -------------------------------------------------------- |
| lastmile.lt | JSON API (`POST` to Cloud Run search service) — **implemented** |
| barbora.lt  | `window.b_productList` JSON inside a `<script>` tag      |
| rimi.lt     | Server-rendered HTML; `data-gtm-eec-product` attributes  |

All three are fetched through the **Oxylabs Scraper API** to handle bot protection. The Oxylabs wrapper lives in `src/scraper/oxylabs.py`. Each store has its own sub-package under `src/scraper/<store>/`.

#### LastMile scraper (`src/scraper/lastmile/`)

| File          | Purpose                                               |
| ------------- | ----------------------------------------------------- |
| `request.py`  | HTTP calls via Oxylabs to fetch categories/products   |
| `types.py`    | Pydantic models for the LastMile JSON API responses   |
| `save.py`     | Persist categories and products to the database       |
| `scraper.py`  | Orchestration: fetch categories, fan-out per top-level category using `ThreadPoolExecutor`, save results |

### Project layout

```
src/
  main.py                    # entry point
  session.py                 # session_scope context manager
  models/
    store.py                 # Store StrEnum (barbora, lastmile, rimi)
    products.py              # Product table (normalised, all stores)
    lastmile_category.py     # LastMileCategory table
    lastmile_product.py      # LastMileProduct table (raw payload)
  queries/
    base.py                  # save_entity helper
    products.py              # get_by_external_id
    lastmile_category.py     # get_by_id
    lastmile_product.py      # get_by_id
  scraper/
    exceptions.py            # ScrapeError, MissingCredentialsError, EmptyResponseError
    oxylabs.py               # post_json wrapper around RealtimeClient
    runner.py                # run_scraper() — top-level orchestrator
    lastmile/                # LastMile store scraper
tests/
  fixtures/
    responses/               # raw JSON API response fixtures
    expected/                # expected output fixtures (e.g. category tree)
  test_lastmile_categories.py
  test_lastmile_products.py
  test_lastmile_scraper.py
migrations/                  # Alembic migrations
```

### Database

PostgreSQL accessed via SQLModel (SQLAlchemy + Pydantic). Three tables:

- **`products`** — normalised product metadata shared across all stores; unique on `(store, external_id)`.
- **`lastmile_categories`** — raw LastMile category data; primary key is the LastMile category ID string.
- **`lastmile_products`** — raw LastMile product payload; primary key is the LastMile product ID string. Nested objects (dimensions, pricing, localised strings) are JSON-stringified into `TEXT` columns.

### Testing

Tests run against an in-memory SQLite database with Alembic migrations applied on each test session. External API calls are replaced with JSON fixtures from `tests/fixtures/responses/`. Run `make test` before submitting changes.

### Session management

`src/session.py` provides a `session_scope` context manager that yields a `Session`. The database URL defaults to `postgresql+psycopg://postgres:postgres@localhost:5433/prep_scout` and can be overridden with the `DATABASE_URL` env var.

### Key environment variables

| Variable             | Default                                                            |
| -------------------- | ------------------------------------------------------------------ |
| `DATABASE_URL`       | `postgresql+psycopg://postgres:postgres@localhost:5433/prep_scout` |
| `REDIS_URL`          | Redis connection URL for publishing events                         |
| `OXYLABS_USERNAME`   | Oxylabs Scraper API username (required at runtime)                 |
| `OXYLABS_PASSWORD`   | Oxylabs Scraper API password (required at runtime)                 |
