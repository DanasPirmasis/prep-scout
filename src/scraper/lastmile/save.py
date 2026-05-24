from sqlmodel import Session

from src.models.lastmile_category import LastMileCategory
from src.models.lastmile_product import LastMileProduct
from src.models.products import Product
from src.models.store import Store
from src.queries import lastmile_category as lastmile_category_queries
from src.queries import lastmile_product as lastmile_product_queries
from src.queries import products as product_queries
from src.queries.base import save_entity
from src.scraper.lastmile.types import (
    LastMileCategoriesResponse,
    LastMileProductPayload,
)


def product(session: Session, data: LastMileProductPayload) -> None:
    existing_product = product_queries.get_by_external_id(session, external_id=data.id, store=Store.LASTMILE)
    if existing_product is None:
        save_entity(
            session,
            Product(
                external_id=data.id,
                store=Store.LASTMILE,
                name=data.name.lt,
                brand=None,
                category=data.category_id,
                unit=data.unit_of_measure,
                comparative_unit=data.conversion_measure,
                price=data.actual_price,
            ),
        )


def last_mile_product(session: Session, payload: LastMileProductPayload) -> None:
    last_mile_product = payload.model_dump()

    name = last_mile_product.pop("name")
    description = last_mile_product.pop("description")

    last_mile_product = LastMileProduct(
        **last_mile_product,
        name_lt=name["lt"],
        name_en=name["en"],
        name_ru=name["ru"],
        description_lt=description["lt"],
        description_en=description["en"],
        description_ru=description["ru"],
    )

    if lastmile_product_queries.get_by_id(session, last_mile_product.id) is None:
        save_entity(session, last_mile_product)

    # Should create event here


def categories(session: Session, data: LastMileCategoriesResponse) -> None:
    for c in data.data:
        payload = c.model_dump()
        name = payload.pop("name")
        payload["metadata_"] = payload.pop("metadata")
        payload["date_last_refresh"] = str(payload["date_last_refresh"])
        category = LastMileCategory(
            **payload,
            name_lt=name["lt"],
            name_en=name["en"],
            name_ru=name["ru"],
        )
        if lastmile_category_queries.get_by_id(session, c.id) is None:
            save_entity(session, category)
