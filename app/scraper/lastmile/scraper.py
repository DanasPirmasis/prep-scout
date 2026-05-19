import base64
import json
import logging
import os
from collections import deque
from typing import cast

from dotenv import load_dotenv
from oxylabs import RealtimeClient
from sqlmodel import Session

from app.models.lastmile_category import LastMileCategory
from app.models.lastmile_product import LastMileProduct
from app.models.products import Product
from app.queries import lastmile_category as lastmile_category_queries
from app.queries import lastmile_product as lastmile_product_queries
from app.queries import products as product_queries
from app.scraper.lastmile.types import (
    LastMileCategoriesResponse,
    LastMileProductsResponse,
)

load_dotenv()

logger = logging.getLogger(__name__)

username = os.getenv("OXYLABS_USERNAME")
password = os.getenv("OXYLABS_PASSWORD")


class MissingCredentialsError(RuntimeError):
    pass


def scrape_lastmile(session: Session) -> None:
    if username is None or password is None:
        raise MissingCredentialsError(
            "OxyLabs credentials not found in environment variables."
        )

    client = RealtimeClient(username, password)
    categories = _get_categories(client)
    category_tree = _build_category_tree(categories)

    _save_categories(session, categories)

    total_categories = len(category_tree)
    scraped_categories = 0

    for parent_id in category_tree:
        products_response = _get_products_in_category(client, parent_id)
        _save_products(session, products_response)
        scraped_categories += 1

    if total_categories > 0:
        completeness = (scraped_categories / total_categories) * 100
        logger.info(
            "Scraped %d/%d categories (%.1f%%)",
            scraped_categories,
            total_categories,
            completeness,
        )


def _save_products(session: Session, data: LastMileProductsResponse) -> None:
    for entry in data["products"]:
        p = entry["frontEndProduct"]
        product = LastMileProduct(
            id=p["id"],
            internal_id=p.get("_id", ""),
            category_id=p.get("categoryId", ""),
            chain_id=p.get("chainId", ""),
            constraint_code=p.get("constraintCode", ""),
            conversion_measure=p.get("conversionMeasure", ""),
            conversion_to_kg=p["conversionToKg"],
            conversion_value=p["conversionValue"],
            country_of_origin=p.get("countryOfOrigin", ""),
            date_created=p.get("dateCreated", ""),
            deposit_price=p["depositPrice"],
            dimensions=dict(p["dimensions"]),
            erp_code=p.get("erpCode", ""),
            has_nutritions=p["hasNutritions"],
            is_active=p["isActive"],
            is_approved=p["isApproved"],
            is_fixed_weight=p["isFixedWeight"],
            is_in_stock=p["isInStock"],
            is_promo=p["isPromo"],
            last_month_lowest_price=p["lastMonthLowestPrice"],
            maximum_order_quantity=p["maximumOrderQuantity"],
            actual_price=p["actualPrice"],
            photo_url=p.get("photoUrl", ""),
            thumb_url=p.get("thumbUrl", ""),
            product_id=p.get("productId", ""),
            prc=dict(p["prc"]),
            cost_price=dict(p["costPrice"]),
            promo=p["promo"],
            promo_tags=p["promoTags"],
            slugs=p["slugs"],
            standard_order_quantity=p["standardOrderQuantity"],
            store_ids=p["storeIds"],
            supplier=p.get("supplier", ""),
            tags=p["tags"],
            unit_of_measure=p.get("unitOfMeasure", ""),
            unit_weight=p["unitWeight"],
            name_lt=p["name"].get("lt", ""),
            name_en=p["name"].get("en", ""),
            name_ru=p["name"].get("ru", ""),
            description_lt=p["description"].get("lt", ""),
            description_en=p["description"].get("en", ""),
            description_ru=p["description"].get("ru", ""),
            allergens=dict(p["allergens"]),
            storing_conditions=dict(p["storingConditions"]),
            ingredients=dict(p["ingredients"]),
            manufacturer_contact=dict(p["manufacturerContact"]),
            safety_information=dict(p["safetyInformation"]),
            product_label=dict(p["productLabel"]),
            nutrition=dict(p["nutrition"]),
        )
        if lastmile_product_queries.get_by_id(session, p["id"]) is None:
            lastmile_product_queries.save_product(session, product)

        existing_product = product_queries.get_by_external_id(
            session, external_id=p["id"], store="lastmile"
        )
        if existing_product is None:
            product_queries.save_product(
                session,
                Product(
                    external_id=p["id"],
                    store="lastmile",
                    name=p["name"].get("lt", ""),
                    brand=p.get("supplier", ""),
                    category=p.get("categoryId", ""),
                    unit=p.get("unitOfMeasure", ""),
                    comparative_unit=p.get("conversionMeasure", ""),
                    price=p["actualPrice"],
                ),
            )


def _save_categories(session: Session, data: LastMileCategoriesResponse) -> None:
    for api_category in data["data"]:
        category = LastMileCategory(
            id=api_category["id"],
            name_lt=api_category["name"].get("lt", ""),
            name_en=api_category["name"].get("en", ""),
            name_ru=api_category["name"].get("ru", ""),
            icon=api_category["icon"],
            icon_url=api_category["iconUrl"],
            thumb_url=api_category["thumbUrl"],
            rank=api_category["rank"],
            parent_id=api_category["parentId"],
            store_ids=api_category["storeIds"],
            chain_id=api_category["chainId"],
            chain_ids=api_category["chainIds"],
            country_ids=api_category["countryIds"],
            picking_rank=api_category["pickingRank"],
            show=api_category["show"],
            mapping=api_category["mapping"],
            minimum_stock=api_category["minimumStock"],
            date_last_refresh=str(api_category["dateLastRefresh"]),
            slugs=api_category["slugs"],
            metadata_=api_category["metadata"],
            seo_title=api_category["seoTitle"],
            seo_description=api_category["seoDescription"],
            category_description=api_category["categoryDescription"],
            subcategories=api_category["subcategories"],
            global_category_id=api_category["globalCategoryId"],
            global_category_parent_id=api_category["globalCategoryParentId"],
        )
        if lastmile_category_queries.get_by_id(session, api_category["id"]) is None:
            lastmile_category_queries.save_category(session, category)


def _get_categories(client: RealtimeClient) -> LastMileCategoriesResponse:
    body = {
        "params": {
            "type": "categories",
            "show": True,
            "chainIds": ["CvKfTzV4TN5U8BTMF1Hl"],
            "storeIds": ["CvKfTzV4TN5U8BTMF1Hl_594"],
        },
        "isUsingCache": True,
        "slim": None,
    }

    response = client.universal.scrape_url(
        url="https://searchservice-952707942140.europe-north1.run.app/categories",
        user_agent_type="desktop_chrome",
        geo_location="Lithuania",
        context=[
            {"key": "http_method", "value": "post"},
            {
                "key": "content",
                "value": base64.b64encode(json.dumps(body).encode()).decode(),
            },
            {"key": "force_headers", "value": True},
            {"key": "headers", "value": {"Content-Type": "application/json"}},
        ],
    )

    raw_content = response.results[0].content
    if raw_content is None:
        raise ValueError("Empty response from LastMile categories endpoint.")
    data = cast(LastMileCategoriesResponse, json.loads(raw_content))
    return data


def _build_category_tree(data: LastMileCategoriesResponse) -> dict[str, list[str]]:
    """
    Builds a flat tree mapping each top-level category ID to all of its descendant IDs.
    Top-level categories are identified by globalCategoryParentId == "0".
    Descendants are collected via BFS using parentId relationships.
    """
    children_by_parent_id: dict[str, list[str]] = {}
    for category in data["data"]:
        parent_id = category["parentId"]
        children_by_parent_id.setdefault(parent_id, []).append(category["id"])

    top_level_categories = [
        category
        for category in data["data"]
        if category["globalCategoryParentId"] == "0"
    ]

    category_tree: dict[str, list[str]] = {}
    for top_level_category in top_level_categories:
        all_descendant_ids: list[str] = []
        bfs_queue: deque[str] = deque([top_level_category["id"]])
        while bfs_queue:
            current_category_id = bfs_queue.popleft()
            direct_children_ids = children_by_parent_id.get(current_category_id, [])
            all_descendant_ids.extend(direct_children_ids)
            bfs_queue.extend(direct_children_ids)
        category_tree[top_level_category["id"]] = all_descendant_ids

    return category_tree


def _get_products_in_category(
    client: RealtimeClient, parent_id: str
) -> LastMileProductsResponse:
    body = {
        "params": {
            "type": "view_products",
            "isActive": True,
            "isApproved": True,
            "chainIds": ["CvKfTzV4TN5U8BTMF1Hl"],
            "categoryIds": [parent_id],
            "filter": {},
            "sort": "karma",
            "isUsingStock": True,
        },
        "limit": 3,
    }

    response = client.universal.scrape_url(
        url="https://searchservice-952707942140.europe-north1.run.app/v1/frontend-products",
        user_agent_type="desktop_chrome",
        geo_location="Lithuania",
        context=[
            {"key": "http_method", "value": "post"},
            {
                "key": "content",
                "value": base64.b64encode(json.dumps(body).encode()).decode(),
            },
            {"key": "force_headers", "value": True},
            {"key": "headers", "value": {"Content-Type": "application/json"}},
        ],
    )

    raw_content = response.results[0].content
    if raw_content is None:
        raise ValueError(f"Empty response for category {parent_id}.")

    return cast(LastMileProductsResponse, json.loads(raw_content))
