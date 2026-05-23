from sqlmodel import Session

from app.models.lastmile_category import LastMileCategory
from app.models.lastmile_product import LastMileProduct
from app.models.products import Product
from app.queries import lastmile_category as lastmile_category_queries
from app.queries import lastmile_product as lastmile_product_queries
from app.queries import products as product_queries
from app.scraper.lastmile.types import (
    LastMileCategoriesResponse,
    LastMileProductPayload,
)


def product(session: Session, data: LastMileProductPayload) -> None:
    existing_product = product_queries.get_by_external_id(session, external_id=data.id, store="lastmile")
    if existing_product is None:
        product_queries.save_product(
            session,
            Product(
                external_id=data.id,
                store="lastmile",
                name=data.name.lt,
                brand=None,
                category=data.category_id,
                unit=data.unit_of_measure,
                comparative_unit=data.conversion_measure,
                price=data.actual_price,
            ),
        )

    pass


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
        lastmile_product_queries.save_product(session, last_mile_product)

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
            lastmile_category_queries.save_category(session, category)
