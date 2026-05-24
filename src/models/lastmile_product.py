from typing import ClassVar

from sqlmodel import Field, SQLModel


class LastMileProduct(SQLModel, table=True):
    __tablename__: ClassVar[str] = "lastmile_products"  # type: ignore[override]

    id: str = Field(primary_key=True)
    internal_id: str
    category_id: str
    chain_id: str
    constraint_code: str
    conversion_measure: str
    conversion_to_kg: float
    conversion_value: float
    country_of_origin: str
    date_created: str
    deposit_price: float
    dimensions: str
    erp_code: str
    has_nutritions: bool
    is_active: bool
    is_approved: bool
    is_fixed_weight: bool
    is_in_stock: bool
    is_promo: bool
    last_month_lowest_price: float
    maximum_order_quantity: int
    actual_price: float
    photo_url: str
    thumb_url: str
    product_id: str
    prc: str
    cost_price: str
    promo: str | None = None
    promo_tags: str
    slugs: str
    standard_order_quantity: int
    store_ids: str
    supplier: str
    tags: str
    unit_of_measure: str
    unit_weight: float
    name_lt: str
    name_en: str
    name_ru: str
    description_lt: str
    description_en: str
    description_ru: str
    allergens: str
    storing_conditions: str
    ingredients: str
    manufacturer_contact: str
    safety_information: str
    product_label: str
    nutrition: str
