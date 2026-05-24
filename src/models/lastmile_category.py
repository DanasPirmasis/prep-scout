from typing import ClassVar

from sqlalchemy import Column, String
from sqlmodel import Field, SQLModel


class LastMileCategory(SQLModel, table=True):
    __tablename__: ClassVar[str] = "lastmile_categories"  # type: ignore[override]

    id: str = Field(primary_key=True)
    name_lt: str
    name_en: str
    name_ru: str
    icon: str
    icon_url: str
    thumb_url: str
    rank: int
    parent_id: str
    store_ids: str
    chain_id: str
    chain_ids: str
    country_ids: str
    picking_rank: int
    show: bool
    mapping: str
    minimum_stock: int | None = None
    date_last_refresh: str
    slugs: str
    metadata_: str = Field(sa_column=Column("metadata", String))
    seo_title: str
    seo_description: str
    category_description: str
    subcategories: str
    global_category_id: str
    global_category_parent_id: str
