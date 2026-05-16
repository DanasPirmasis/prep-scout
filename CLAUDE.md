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

# Run the scheduler
python -m app.main

# Install dependencies
uv sync
```

## Architecture

**prep-scout** is one service in a multi-service system. It scrapes grocery prices from three Lithuanian e-commerce stores (Barbora.lt, Rimi.lt, LastMile.lt), stores products in its own PostgreSQL database, and publishes events to Redis Streams for downstream services.

### Responsibilities

prep-scout is responsible for scraping and publishing only. Price history, cross-store matching, and user-facing features live in other services.

### Data flow

1. `app/scraper/runner.py` — daily job entry point (stub; scrapers not yet implemented). Called by APScheduler at 2 AM UTC from `app/main.py`.
2. Scrapers read the existing product by `(store, external_id)`. If not found → insert and publish `product.created`. If found → update and publish `product.updated`.

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
| lastmile.lt | JSON API (`POST` to Cloud Run search service)            |
| barbora.lt  | `window.b_productList` JSON inside a `<script>` tag      |
| rimi.lt     | Server-rendered HTML; `data-gtm-eec-product` attributes  |

All three are fetched through the **Oxylabs Scraper API** to handle bot protection. Each site needs its own parser behind a common interface (see `init.md` for the planned `scrapers/base.py` structure).

### Database

PostgreSQL accessed via SQLModel (SQLAlchemy + Pydantic). One table:

- **`products`** — product metadata; unique on `(store, external_id)`.

### Session management

`app/session.py` provides a `get_session` generator for use as a FastAPI dependency. The database URL defaults to `postgresql+psycopg://postgres:postgres@localhost:5433/prep_scout` and can be overridden with the `DATABASE_URL` env var.

### Key environment variables

| Variable       | Default                                                            |
| -------------- | ------------------------------------------------------------------ |
| `DATABASE_URL` | `postgresql+psycopg://postgres:postgres@localhost:5433/prep_scout` |
| `REDIS_URL`    | Redis connection URL for publishing events                         |
