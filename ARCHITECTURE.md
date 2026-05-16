# Architecture Notes

## Services

| Service        | Responsibility                                                |
| -------------- | ------------------------------------------------------------- |
| **prep-scout** | Scrapes raw product/price data, stores products in its own DB |
| **prep-link**  | Consumes new products, runs LLM matching across stores        |
| **prep**       | User-facing app with its own DB and unrelated domain logic    |
| **Redis**      | Event bus — owned by infra, not any application repo          |

## Event Flow

```
                                    prep-link
                                   (LLM matching)
                          created ──product.matched──> prep
                         /                              │
prep-scout ─────────────>                               │
(scraping)               \                              │
                          created + updated ────────────>prep
```

1. prep-scout scrapes a new product → publishes `product.created`
2. prep-scout scrapes a known product → publishes `product.updated`
3. prep-link consumes `product.created` only → runs LLM cross-store matching → publishes `product.matched`
4. prep consumes `product.created` → writes product row, `canonical_id = null`
5. prep consumes `product.updated` → updates product row, appends `price_history` row
6. prep consumes `product.matched` → sets `canonical_id` on matching product rows

prep shows unmatched products immediately; cross-store comparison unlocks once `product.matched` arrives. The join key into prep's tables is `(store, external_id)`, carried in all prep-scout events.

Price history lives in prep, not prep-scout. No service calls another's API or shares a database.

## Events

### `product.created` (published by prep-scout)

Consumed by: prep-link, prep

| Field              | Description                       |
| ------------------ | --------------------------------- |
| `store`            | `barbora`, `rimi`, or `lastmile`  |
| `external_id`      | Store-specific product identifier |
| `name`             | Product name                      |
| `brand`            | Brand name                        |
| `category`         | Store category                    |
| `unit`             | Unit of measure                   |
| `comparative_unit` | Unit price basis (e.g. €/kg)      |
| `price`            | Current effective price           |

### `product.updated` (published by prep-scout)

Consumed by: prep

| Field              | Description                       |
| ------------------ | --------------------------------- |
| `store`            | `barbora`, `rimi`, or `lastmile`  |
| `external_id`      | Store-specific product identifier |
| `name`             | Product name                      |
| `brand`            | Brand name                        |
| `category`         | Store category                    |
| `unit`             | Unit of measure                   |
| `comparative_unit` | Unit price basis (e.g. €/kg)      |
| `price`            | Current effective price           |

### `product.matched` (published by prep-link)

Consumed by: prep

| Field          | Description                                     |
| -------------- | ----------------------------------------------- |
| `canonical_id` | prep-link's stable cross-store product identity |
| `confidence`   | Match confidence score                          |
| `products`     | List of matched `(store, external_id)` pairs    |

## prep-link Data Model

**`products`** — read-only projection of prep-scout's products, built from `product.created` events; mirrors prep-scout's schema

| Field              | Description                      |
| ------------------ | -------------------------------- |
| `id`               | Internal PK                      |
| `store`            | `barbora`, `rimi`, or `lastmile` |
| `external_id`      | Store-specific identifier        |
| `name`             | Product name                     |
| `brand`            | Brand name                       |
| `category`         | Store's raw category name        |
| `unit`             | Unit of measure                  |
| `comparative_unit` | Unit price basis (e.g. €/kg)     |
| `price`            | Current effective price          |

**`store_category_mappings`** — manual table mapping each store's category names to a canonical category; required before LLM matching can run

| Field               | Description                      |
| ------------------- | -------------------------------- |
| `id`                | Internal PK                      |
| `store`             | `barbora`, `rimi`, or `lastmile` |
| `store_category`    | Raw category name from the store |
| `canonical_category`| Shared canonical category name   |

**`product_mappings`** — output of LLM matching; cross-store canonical product links

| Field          | Description                                    |
| -------------- | ---------------------------------------------- |
| `id`           | Internal PK (used as `canonical_id` in events) |
| `product_id_a` | FK → products                                  |
| `product_id_b` | FK → products                                  |
| `source`       | `auto` or `manual`                             |
| `confidence`   | LLM confidence score (0–1)                     |

Confidence routing: auto-link above 0.9, auto-reject below 0.1, manual review in between. Manual overrides always win.

## Ownership

| Concern              | Owner                         |
| -------------------- | ----------------------------- |
| Redis instance       | infra / shared docker-compose |
| Stream name contract | agreed between repos          |
| `product.created`    | prep-scout                    |
| `product.updated`    | prep-scout                    |
| `product.matched`    | prep-link                     |
