# Scraper — Project Structure & Libraries

## Libraries

| Concern            | Library                   |
| ------------------ | ------------------------- |
| Scraping           | `oxylabs`                 |
| HTML parsing       | `beautifulsoup4` + `lxml` |
| PostgreSQL         | `psycopg` (v3)            |
| Migrations         | `alembic`                 |
| LLM matching       | `anthropic`               |
| Package management | `uv`                      |

## Project Structure

```
scraper/
  scrapers/
    base.py
    barbora.py
    rimi.py
    lastmile.py
  db/
    repository.py
    migrations/
  matcher/
    llm.py
  main.py
  pyproject.toml
```
