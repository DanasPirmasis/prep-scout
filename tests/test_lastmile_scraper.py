import json
from pathlib import Path
from typing import cast

import pytest
from oxylabs import RealtimeClient
from sqlmodel import Session

from src.scraper.lastmile import scraper
from src.scraper.lastmile.scraper import _build_category_tree
from src.scraper.lastmile.types import (
    LastMileCategoriesResponse,
    LastMileProductEntry,
    LastMileProductPayload,
    LastMileProductsResponse,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CATEGORIES_FIXTURE = PROJECT_ROOT / "tests" / "fixtures" / "responses" / "lastmile-categories.json"
EXPECTED_CATEGORY_TREE_FIXTURE = PROJECT_ROOT / "tests" / "fixtures" / "expected" / "lastmile-category-tree.json"
PRODUCTS_FIXTURE = PROJECT_ROOT / "tests" / "fixtures" / "responses" / "lastmile-frontend-products.json"


def _first_product_payload() -> LastMileProductPayload:
    product_data = json.loads(PRODUCTS_FIXTURE.read_text())["products"][0]["frontEndProduct"]
    return LastMileProductPayload.model_validate(product_data)


def test_build_category_tree_groups_top_level_categories_with_all_descendants() -> None:
    response = LastMileCategoriesResponse.model_validate_json(CATEGORIES_FIXTURE.read_text())
    expected_category_tree = json.loads(EXPECTED_CATEGORY_TREE_FIXTURE.read_text())

    category_tree = _build_category_tree(response)

    assert category_tree == expected_category_tree


def test_scrape_lastmile_fetches_and_saves_categories_and_products(monkeypatch: pytest.MonkeyPatch) -> None:
    session = cast(Session, object())
    client = cast(RealtimeClient, object())

    categories_response = LastMileCategoriesResponse.model_validate_json(CATEGORIES_FIXTURE.read_text())

    product_payload = _first_product_payload()
    products_response = LastMileProductsResponse(
        status="success",
        products=[LastMileProductEntry(front_end_product=product_payload, position=1, karma_adjustment=0)],
        count=1,
    )

    expected_category_ids = set(_build_category_tree(categories_response))
    expected_products = [entry.front_end_product for entry in products_response.products]

    print(f"Testing scrape_lastmile with {len(expected_category_ids)} top-level categories")
    print(f"Expected product category requests: {sorted(expected_category_ids)}")
    print(f"Mocked products returned per category: {[product.id for product in expected_products]}")

    saved_categories: list[tuple[Session, LastMileCategoriesResponse]] = []
    requested_product_categories: list[str] = []
    saved_lastmile_products: list[tuple[Session, LastMileProductPayload]] = []
    saved_products: list[tuple[Session, LastMileProductPayload]] = []

    def get_categories(fake_client: RealtimeClient) -> LastMileCategoriesResponse:
        assert fake_client is client
        return categories_response

    def get_products_in_category(fake_client: RealtimeClient, category_id: str) -> LastMileProductsResponse:
        assert fake_client is client
        requested_product_categories.append(category_id)
        return products_response

    def save_categories(fake_session: Session, response: LastMileCategoriesResponse) -> None:
        saved_categories.append((fake_session, response))

    def save_lastmile_product(fake_session: Session, product: LastMileProductPayload) -> None:
        saved_lastmile_products.append((fake_session, product))

    def save_product(fake_session: Session, product: LastMileProductPayload) -> None:
        saved_products.append((fake_session, product))

    monkeypatch.setattr(scraper.request, "get_categories", get_categories)
    monkeypatch.setattr(scraper.request, "get_products_in_category", get_products_in_category)
    monkeypatch.setattr(scraper.save, "categories", save_categories)
    monkeypatch.setattr(scraper.save, "last_mile_product", save_lastmile_product)
    monkeypatch.setattr(scraper.save, "product", save_product)

    scraper.scrape_lastmile(session, client)

    print(f"Saved category response count: {len(saved_categories)}")
    print(f"Actual product category requests: {sorted(requested_product_categories)}")
    print(f"LastMile product save calls: {len(saved_lastmile_products)}")
    print(f"Generic product save calls: {len(saved_products)}")

    assert saved_categories == [(session, categories_response)], (
        "scrape_lastmile should save the category response before scraping products"
    )
    assert set(requested_product_categories) == expected_category_ids, (
        "scrape_lastmile should request products for every top-level category from the category tree"
    )
    assert len(requested_product_categories) == len(expected_category_ids), (
        "scrape_lastmile should request each top-level category exactly once"
    )
    assert saved_lastmile_products == [
        (session, product) for _ in expected_category_ids for product in expected_products
    ], "scrape_lastmile should save each fetched payload as a LastMileProduct"
    assert saved_products == [(session, product) for _ in expected_category_ids for product in expected_products], (
        "scrape_lastmile should also save each fetched payload as a generic Product"
    )
