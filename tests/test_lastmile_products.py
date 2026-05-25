import json
from pathlib import Path

from sqlalchemy import func
from sqlmodel import Session, select

from src.models.lastmile_product import LastMileProduct
from src.models.products import Product
from src.models.store import Store
from src.scraper.lastmile import save
from src.scraper.lastmile.types import LastMileProductPayload

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PRODUCTS_FIXTURE = PROJECT_ROOT / "tests" / "fixtures" / "responses" / "lastmile-frontend-products.json"


def _first_product_payload() -> LastMileProductPayload:
    product_data = json.loads(PRODUCTS_FIXTURE.read_text())["products"][0]["frontEndProduct"]
    return LastMileProductPayload.model_validate(product_data)


def test_lastmile_product_is_processed_and_saved(session: Session) -> None:
    expected_product = _first_product_payload()

    save.last_mile_product(session, expected_product)

    product_count = session.exec(select(func.count()).select_from(LastMileProduct)).one()
    product = session.get(LastMileProduct, expected_product.id)

    assert product_count == 1
    assert product is not None
    assert product.internal_id == expected_product.internal_id
    assert product.category_id == expected_product.category_id
    assert product.chain_id == expected_product.chain_id
    assert product.constraint_code == expected_product.constraint_code
    assert product.conversion_measure == expected_product.conversion_measure
    assert product.conversion_to_kg == expected_product.conversion_to_kg
    assert product.conversion_value == expected_product.conversion_value
    assert product.country_of_origin == expected_product.country_of_origin
    assert product.date_created == expected_product.date_created
    assert product.deposit_price == expected_product.deposit_price
    assert product.erp_code == expected_product.erp_code
    assert product.has_nutritions == expected_product.has_nutritions
    assert product.is_active == expected_product.is_active
    assert product.is_approved == expected_product.is_approved
    assert product.is_fixed_weight == expected_product.is_fixed_weight
    assert product.is_in_stock == expected_product.is_in_stock
    assert product.is_promo == expected_product.is_promo
    assert product.last_month_lowest_price == expected_product.last_month_lowest_price
    assert product.maximum_order_quantity == expected_product.maximum_order_quantity
    assert product.actual_price == expected_product.actual_price
    assert product.photo_url == expected_product.photo_url
    assert product.thumb_url == expected_product.thumb_url
    assert product.product_id == expected_product.product_id
    assert product.standard_order_quantity == expected_product.standard_order_quantity
    assert product.supplier == expected_product.supplier
    assert product.unit_of_measure == expected_product.unit_of_measure
    assert product.unit_weight == expected_product.unit_weight
    assert product.name_lt == expected_product.name.lt
    assert product.name_en == expected_product.name.en
    assert product.name_ru == expected_product.name.ru
    assert product.description_lt == expected_product.description.lt
    assert product.description_en == expected_product.description.en
    assert product.description_ru == expected_product.description.ru
    assert json.loads(product.dimensions) == expected_product.dimensions.model_dump()
    assert json.loads(product.prc) == expected_product.prc.model_dump()
    assert json.loads(product.cost_price) == expected_product.cost_price.model_dump()
    assert json.loads(product.promo_tags) == expected_product.promo_tags
    assert json.loads(product.slugs) == expected_product.slugs
    assert json.loads(product.store_ids) == expected_product.store_ids
    assert json.loads(product.tags) == expected_product.tags
    assert json.loads(product.allergens) == expected_product.allergens.model_dump()
    assert json.loads(product.storing_conditions) == expected_product.storing_conditions.model_dump()
    assert json.loads(product.ingredients) == expected_product.ingredients.model_dump()
    assert json.loads(product.manufacturer_contact) == expected_product.manufacturer_contact.model_dump()
    assert json.loads(product.safety_information) == expected_product.safety_information.model_dump()
    assert json.loads(product.product_label) == expected_product.product_label.model_dump()
    assert json.loads(product.nutrition) == expected_product.nutrition.model_dump()

    save.last_mile_product(session, expected_product)

    product_count_after_second_save = session.exec(select(func.count()).select_from(LastMileProduct)).one()
    assert product_count_after_second_save == 1


def test_product_is_processed_and_saved(session: Session) -> None:
    expected_product = _first_product_payload()

    save.product(session, expected_product)

    product_count = session.exec(select(func.count()).select_from(Product)).one()
    product = session.exec(
        select(Product).where(Product.external_id == expected_product.id, Product.store == Store.LASTMILE)
    ).one_or_none()

    assert product_count == 1
    assert product is not None
    assert product.external_id == expected_product.id
    assert product.store == Store.LASTMILE
    assert product.name == expected_product.name.lt
    assert product.brand is None
    assert product.category == expected_product.category_id
    assert product.unit == expected_product.unit_of_measure
    assert product.comparative_unit == expected_product.conversion_measure
    assert product.price == expected_product.actual_price

    save.product(session, expected_product)

    product_count_after_second_save = session.exec(select(func.count()).select_from(Product)).one()
    assert product_count_after_second_save == 1
