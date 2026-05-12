# Grocery Scraper — Design Notes

## Sites & Protection

| Site        | Protection                | Difficulty |
| ----------- | ------------------------- | ---------- |
| barbora.lt  | Cloudflare Bot Management | Hard       |
| rimi.lt     | Uzumaki behavioral        | Medium     |
| lastmile.lt | None                      | Easy       |

All three handled via **Oxylabs Scraper API**

## Scraping Approach

- Scrape category list pages
- Barbora/LastMile: up to ~5 pages per category. Rimi: up to 42 pages per category.
- **Daily runs** are sufficient
- List pages return enough: name, price, unit price, availability

## Data Delivery Per Site

| Site        | Format                                          | Notes                                                            |
| ----------- | ----------------------------------------------- | ---------------------------------------------------------------- |
| lastmile.lt | JSON API                                        | Clean, direct                                                    |
| barbora.lt  | JSON in `<script>` tag (`window.b_productList`) | Parse script tag, then JSON                                      |
| rimi.lt     | Server-rendered HTML                            | `data-gtm-eec-product` JSON attribute on `.js-product-container` |

### Barbora.lt Endpoints

- **Products:** `window.b_productList` JSON blob in a `<script>` tag on category list pages — no XHR, parse HTML via Oxylabs
- **Add to cart:** `POST https://barbora.lt/api/eshop/v1/cart/item?returnCartInfo=true`
  - Auth: **Cookie-based** — `.BRBAUTH` = Barbora-issued JWT (`iss: "Barbora"`, `aud: "BarboraServices"`, `sid` = user GUID). Set on login; no Bearer header.
  - Also requires: `cf_clearance` (Cloudflare — handled by Oxylabs), `AWSALB*` stickiness cookies (set by ALB on first request)
  - Request body:

```json
{
  "product_id": "000000000000068728",
  "quantity": 1,
  "unit": 0,
  "web_url": "https://barbora.lt/<category-slug>/<product-slug>"
}
```

- `product_id` is zero-padded to 18 digits — verify whether `window.b_productList.id` is already this format
- `web_url` is required — store the product page path alongside `external_id` in the scraper's products table
- **Cart discovery:** Not needed. Cart is server-side and user-bound — no cart ID in any request, just authenticate with `.BRBAUTH` cookie.
- **Cart write (MVP):** No — Barbora uses Google/Facebook OAuth; `.BRBAUTH` only obtainable via browser session. Browser extension post-MVP.

### LastMile.lt Endpoints

- **Products:** `POST https://searchservice-952707942140.europe-north1.run.app/v1/frontend-products`
- **Add to cart:** `PATCH https://firestore.googleapis.com/v1/projects/lastmile-delivery/databases/(default)/documents/carts/{cartId}` with `Authorization: Bearer {Firebase ID token}`

```json
{
  "writes": [
    {
      "update": {
        "name": "projects/lastmile-delivery/databases/(default)/documents/carts/{cartId}",
        "fields": {
          "items": {
            "mapValue": {
              "fields": {
                "{productFirebaseId}": {
                  "mapValue": {
                    "fields": {
                      "quantity": { "integerValue": "1" },
                      "dateCreated": { "timestampValue": "2026-05-11T18:19:39.602000000Z" }
                    }
                  }
                }
              }
            }
          },
          "dateLastRefresh": { "timestampValue": "2026-05-11T18:19:39.602000000Z" }
        }
      },
      "updateMask": {
        "fieldPaths": [
          "dateLastRefresh",
          "items.{productFirebaseId}.dateCreated",
          "items.{productFirebaseId}.quantity"
        ]
      }
    }
  ]
}
```

- `cartId` is **not** the user's Firebase UID — look it up via a Firestore `runQuery` filtering `carts` by `userId` and `isCheckedOut: false`. See `last-mile.md`.
- `productFirebaseId` must be stored alongside `external_id` in the scraper's `products` table.
- **Cart write (MVP):** Yes — Firebase API keys are public; use `signInWithPopup` (Google OAuth) in our frontend to get an ID token. No browser extension needed.

### Rimi.lt Endpoints

- **Products:** Server-rendered HTML on category pages — no JSON API. Parse `data-gtm-eec-product` attribute on `.js-product-container` elements via Oxylabs.
- **Category URL pattern:** `https://www.rimi.lt/e-parduotuve/lt/produktai/{category-hierarchy}/c/{category-id}`
- **Pagination:** `?currentPage=N` (1-indexed). Stop when page contains no `.js-product-container` elements.
- **Full category list:** `https://www.rimi.lt/e-parduotuve/sitemaps/categories/siteMap_rimiLtSite_Category_lt_1.xml`
- **Add to cart:** `PUT https://www.rimi.lt/e-parduotuve/cart/change`
  - Auth: **Cookie + CSRF** — `rimi_storefront_session` + `laravel_session` cookies; `X-XSRF-TOKEN` header (URL-decoded value of the `XSRF-TOKEN` cookie)
  - Also requires: `X-Cart-Update-Timestamp` (current Unix ms), `X-Requested-With: XMLHttpRequest`, `uzlc` Uzumaki header (Oxylabs)
  - Request body:

```json
{ "_method": "put", "product": "183737", "amount": "1" }
```

- `product` = `data-gtm-eec-product.id` as a string. `amount` = quantity as a string. Set `"amount": "0"` to remove.
- No cart ID — cart is server-side and session-bound.
- **Cart write (MVP):** No — login goes through `sso.onrimi.net` and requires reCAPTCHA v3 + email OTP; server-side automation not practical. Browser extension post-MVP (same as Barbora).

Each site needs its own parser implementation behind a common interface.

## Cart Write Summary

| Store       | MVP | Method                             | Auth                                    |
| ----------- | --- | ---------------------------------- | --------------------------------------- |
| lastmile.lt | Yes | Firestore REST PATCH               | Firebase ID token (Google OAuth)        |
| barbora.lt  | No  | POST to Barbora cart API           | `.BRBAUTH` cookie — extension only      |
| rimi.lt     | No  | PUT to `/e-parduotuve/cart/change` | Session cookies + CSRF — extension only |

## Data Model

**`products`** — metadata, rarely changes

- `id`, `external_id`, `store`, `name`, `brand`, `category`, `unit`, `comparative_unit`
- Unique on `(store, external_id)`

**`price_history`** — one row per daily scrape per product

- `id`, `product_id` (FK), `price`, `retail_price`, `special_price`, `is_available`, `scraped_at`

**`product_mappings`** — cross-store canonical links

- `id`, `product_id_a`, `product_id_b`, `source` (auto/manual), `confidence`

## Per-Site Field Mapping

| Field         | LastMile                      | Barbora                                 | Rimi                                                                                            |
| ------------- | ----------------------------- | --------------------------------------- | ----------------------------------------------------------------------------------------------- |
| External ID   | `productId`                   | `id` (zero-padded to 18 digits)         | `data-gtm-eec-product.id` (numeric string)                                                      |
| Name          | `name.lt`                     | `title`                                 | `data-gtm-eec-product.name`                                                                     |
| Brand         | in name string                | `brand_name`                            | `data-gtm-eec-product.brand` (frequently null)                                                  |
| Price         | `prc.p`                       | `price` (effective, already discounted) | `data-gtm-eec-product.price`                                                                    |
| Retail price  | —                             | `units[0].retail_price`                 | — (not exposed)                                                                                 |
| Loyalty price | `prc.l` / `prc.ltill`         | via `promotion.type == LOYALTY_PRICE`   | — (no loyalty system)                                                                           |
| Unit price    | derived from `conversionToKg` | `comparative_unit_price`                | `.card__price-per .sr-only` — `"Kaina už vienetą: 2,50 €/kg"`, strip label, normalize `,` → `.` |
| Unit          | `unitOfMeasure`               | `comparative_unit`                      | second aria-hidden span in `.card__price-per` (e.g. `€/kg`)                                     |
| Available     | `isInStock`                   | `status == "active"`                    | presence of `.js-add-to-cart` form                                                              |
| Cart key      | `productFirebaseId`           | `id` (zero-padded, as `product_id`)     | `data-gtm-eec-product.id` (as `product` string)                                                 |
| Cart URL      | —                             | product page path (stored as `web_url`) | — (no cart write for MVP)                                                                       |

## Cross-Store Product Matching

No site exposes EAN barcodes in list responses — can't use that for barcode matching.

### Category Mapping

Store categories are named differently across stores (e.g. Barbora "Grietinė ir kastinys", Rimi "Grietinė", LastMile "Grietinė and grietinėlė"). Solved with a **manual `store_category_mappings` table** — one-time work linking each store's categories to a canonical category.

Category renames are caught by monitoring: zero products in a previously populated canonical category triggers an alert.

### LLM Matching Pipeline

1. **Pre-filter by canonical category** — only compare products within the same canonical category across stores
2. **Send all pairs within a category to LLM in batches** — ask for `{ match, confidence, reason }` per pair
3. **Confidence routing** — auto-link above 0.9, auto-reject below 0.1, manual review in between
4. **Cache results** in `product_mappings` — only runs on new products, not re-run on every scrape

Initial bulk run covers all categories at once. Estimated cost: a few dollars at Haiku pricing for the full catalog.

**Model:** Start with **Claude Haiku 4.5** — task is simple, cost is negligible at this scale. Local models (Llama 3.1 8B via Ollama) are viable but Lithuanian language quality is uncertain — test before committing.

**Manual override table** — corrections layer, always wins over automated results.

## Monitoring

- Oxylabs handles request-level failures
- Application assertion: alert if scraped product count per category drops below expected threshold
