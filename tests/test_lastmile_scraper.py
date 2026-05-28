import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import cast

import pytest
from oxylabs import RealtimeClient
from pydantic import ValidationError
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


@dataclass
class _LastMileScraperStubs:
    session: Session
    client: RealtimeClient
    categories_response: LastMileCategoriesResponse
    products_response: LastMileProductsResponse
    failed_category_id: str | None = None
    saved_categories: list[tuple[Session, LastMileCategoriesResponse]] = field(default_factory=list)
    requested_product_categories: list[str] = field(default_factory=list)
    saved_lastmile_products: list[tuple[Session, LastMileProductPayload]] = field(default_factory=list)
    saved_products: list[tuple[Session, LastMileProductPayload]] = field(default_factory=list)

    def get_categories(self, stub_client: RealtimeClient) -> LastMileCategoriesResponse:
        assert stub_client is self.client
        return self.categories_response

    def get_products_in_category(self, stub_client: RealtimeClient, category_id: str) -> LastMileProductsResponse:
        assert stub_client is self.client
        self.requested_product_categories.append(category_id)
        if category_id == self.failed_category_id:
            raise RuntimeError("fetch failed")
        return self.products_response

    def save_categories(self, stub_session: Session, response: LastMileCategoriesResponse) -> None:
        self.saved_categories.append((stub_session, response))

    def save_lastmile_product(self, stub_session: Session, product: LastMileProductPayload) -> None:
        self.saved_lastmile_products.append((stub_session, product))

    def save_product(self, stub_session: Session, product: LastMileProductPayload) -> None:
        self.saved_products.append((stub_session, product))

    def install(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(scraper.request, "get_categories", self.get_categories)
        monkeypatch.setattr(scraper.request, "get_products_in_category", self.get_products_in_category)
        monkeypatch.setattr(scraper.save, "categories", self.save_categories)
        monkeypatch.setattr(scraper.save, "last_mile_product", self.save_lastmile_product)
        monkeypatch.setattr(scraper.save, "product", self.save_product)


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

    stubs = _LastMileScraperStubs(session, client, categories_response, products_response)
    stubs.install(monkeypatch)

    scraper.scrape_lastmile(session, client)

    print(f"Saved category response count: {len(stubs.saved_categories)}")
    print(f"Actual product category requests: {sorted(stubs.requested_product_categories)}")
    print(f"LastMile product save calls: {len(stubs.saved_lastmile_products)}")
    print(f"Generic product save calls: {len(stubs.saved_products)}")

    assert stubs.saved_categories == [(session, categories_response)], (
        "scrape_lastmile should save the category response before scraping products"
    )
    assert set(stubs.requested_product_categories) == expected_category_ids, (
        "scrape_lastmile should request products for every top-level category from the category tree"
    )
    assert len(stubs.requested_product_categories) == len(expected_category_ids), (
        "scrape_lastmile should request each top-level category exactly once"
    )
    expected_lastmile_product_saves = [
        (session, product) for _ in expected_category_ids for product in expected_products
    ]
    assert sorted(stubs.saved_lastmile_products, key=lambda x: x[1].id) == sorted(
        expected_lastmile_product_saves, key=lambda x: x[1].id
    ), "scrape_lastmile should save each fetched payload as a LastMileProduct"

    expected_product_saves = [(session, product) for _ in expected_category_ids for product in expected_products]
    assert sorted(stubs.saved_products, key=lambda x: x[1].id) == sorted(
        expected_product_saves, key=lambda x: x[1].id
    ), "scrape_lastmile should also save each fetched payload as a generic Product"


def test_scrape_lastmile_skips_category_when_product_fetch_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    session = cast(Session, object())
    client = cast(RealtimeClient, object())

    categories_response = LastMileCategoriesResponse.model_validate_json(CATEGORIES_FIXTURE.read_text())
    category_ids = set(_build_category_tree(categories_response))
    failed_category_id = next(iter(category_ids))

    product_payload = _first_product_payload()
    products_response = LastMileProductsResponse(
        status="success",
        products=[LastMileProductEntry(front_end_product=product_payload, position=1, karma_adjustment=0)],
        count=1,
    )

    stubs = _LastMileScraperStubs(session, client, categories_response, products_response, failed_category_id)
    stubs.install(monkeypatch)

    scraper.scrape_lastmile(session, client)

    assert set(stubs.requested_product_categories) == category_ids
    assert len(stubs.saved_lastmile_products) == len(category_ids) - 1
    assert len(stubs.saved_products) == len(category_ids) - 1


def test_lastmile_products_response_rejects_null_for_required_product_string() -> None:
    response_data = json.loads(PRODUCTS_FIXTURE.read_text())
    response_data["products"][0]["frontEndProduct"]["countryOfOrigin"] = None

    with pytest.raises(ValidationError) as exc_info:
        LastMileProductsResponse.model_validate(response_data)

    assert exc_info.value.errors()[0]["loc"] == ("products", 0, "frontEndProduct", "countryOfOrigin")
    assert exc_info.value.errors()[0]["type"] == "string_type"
