# Code Review TODOs

## Efficiency

- **Sequential HTTP fetch dominates wall time** (`app/scraper/lastmile/scraper.py:30-39`). TODO comment already in place. Fix with `ThreadPoolExecutor` (Oxylabs realtime is sync but thread-safe) or switch to Oxylabs Push-Pull.
- **One session + 2 commits + 2 refreshes per product** (`scraper.py:33-37`, query helpers). For thousands of products this is ~10k+ round-trips, ~4k+ fsyncs. Move `with session_factory()` outside the inner loop; drop `commit()`/`refresh()` from query helpers; commit once per batch.
- **N+1 existence-check + insert** in all three `save_*` paths. Use Postgres `INSERT ... ON CONFLICT ... DO UPDATE ... RETURNING (xmax = 0)` — one round-trip and tells you create vs. update for the event emission.
- **`session.refresh()` in query helpers is wasted** — return values are discarded.
- **`save.categories` commits per category** — use `add_all` + single commit.

## Code quality

- **Stray `pass`** at end of `save.product()` (`save.py:34`); missing `-> None`.
- **Variable rebinding** in `save.last_mile_product` — `product` is bound to a dict, then rebound to a `LastMileProduct` (`save.py:38, 43`). Use `payload` / `row`.
- **Naming**: `save.product` / `save.categories` (nouns) read awkwardly as actions; consider `upsert_product` etc. Also `save.product` shadows the local `product` variable in `scraper.py:34-37`.
- **TODO-as-prose comments** — `# Ideally this should execute all of the requests at the same time.` and `# Should create event here`. Either `# TODO:` or tracked issues.
- **Stringly-typed `store="lastmile"`** duplicated in `save.py:17, 24`. With 3 stores planned, an enum/constant avoids typos.
- **`metadata` → `metadata_` and `date_last_refresh` → `str` coercions** leak SQLModel column quirks into `save.py:63-64`. Suggest `LastMileCategory.from_payload(...)` classmethod, or column alias.
- **`return None`** at `scraper.py:27` — bare `return` is more idiomatic.

## Code reuse

- **`request.py` near-duplicate POST helpers** — `get_categories` and `get_products_in_category` share ~12 lines of OxyLabs context-building boilerplate. Extract `_post_json(client, url, body)`.
- **`request.py` hardcoded chain/store IDs** (`"CvKfTzV4TN5U8BTMF1Hl"`, `"CvKfTzV4TN5U8BTMF1Hl_594"`) duplicated. Lift to module constants.
- **Query helpers `save_category` / `save_product` are byte-identical** across three files (`add` + `commit` + `refresh` + `return`). One generic `save(session, instance)` helper would dedupe.
- **`get_by_id` for PK lookups** could just use `session.get(Model, id)` — SQLModel/SQLAlchemy's PK shortcut.
- **`MissingCredentialsError`** is a 2-line file in `app/scraper/exceptions.py`, imported only by `runner.py`. Either inline at the raise site, or grow the module with `ScrapeError`, `EmptyResponseError` (currently raised as bare `ValueError` in `request.py:41, 79`).

## Pydantic types (`types.py`)

- **`LocalizedString.de`** is declared but never read in save logic — dead field, no `*_de` columns.
- **`ProductNutrition` / `ProductPrice` / `ProductDimensions`** lack `model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)` that the other models use. `ProductNutrition.satFat` is camelCase Python attr, inconsistent with the rest of the file. Note: changing this affects the shape of the dumped JSON stored in the `nutrition`/`prc`/`cost_price` JSON columns — possible data-format change.
- **`ProductPrice.ltill: str | None`** while all sibling fields are `float | None`. Possible parse bug; verify against a sample payload.
- **`l: float | None # noqa: E741`** — better to give the attribute a meaningful name and alias to `"l"`.
- **Generic `dict` / `list`** types on many model fields (`mapping`, `metadata`, `seo_title`, `subcategories`, `tags`, `promo_tags`) — Pydantic gains nothing over `dict[str, Any]` / `list[Any]`. Either model them or annotate explicitly.

## Robustness

- **`response.results[0]`** assumes non-empty results (`request.py:39, 77`). Add `len(...) == 0` guard so failures raise the typed error instead of `IndexError`.

## Minor

- Commented-out APScheduler block in `main.py` — delete or wire behind a flag.
- `_log_completeness` is a 3-line helper for one call site — inline; also missing `-> None`.
