from typing import ClassVar

from sqlalchemy import JSON, Column
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
    dimensions: dict = Field(sa_column=Column(JSON))
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
    prc: dict = Field(sa_column=Column(JSON))
    cost_price: dict = Field(sa_column=Column(JSON))
    promo: dict | None = Field(default=None, sa_column=Column(JSON, nullable=True))
    promo_tags: dict = Field(sa_column=Column(JSON))
    slugs: list = Field(sa_column=Column(JSON))
    standard_order_quantity: int
    store_ids: list = Field(sa_column=Column(JSON))
    supplier: str
    tags: list = Field(sa_column=Column(JSON))
    unit_of_measure: str
    unit_weight: float
    name_lt: str
    name_en: str
    name_ru: str
    description_lt: str
    description_en: str
    description_ru: str
    allergens: dict = Field(sa_column=Column(JSON))
    storing_conditions: dict = Field(sa_column=Column(JSON))
    ingredients: dict = Field(sa_column=Column(JSON))
    manufacturer_contact: dict = Field(sa_column=Column(JSON))
    safety_information: dict = Field(sa_column=Column(JSON))
    product_label: dict = Field(sa_column=Column(JSON))
    nutrition: dict = Field(sa_column=Column(JSON))
