from typing import ClassVar

from sqlalchemy import JSON, Column
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
    store_ids: list = Field(sa_column=Column(JSON))
    chain_id: str
    chain_ids: list = Field(sa_column=Column(JSON))
    country_ids: list = Field(sa_column=Column(JSON))
    picking_rank: int
    show: bool
    mapping: dict = Field(sa_column=Column(JSON))
    minimum_stock: int | None = None
    date_last_refresh: str
    slugs: list = Field(sa_column=Column(JSON))
    metadata_: dict = Field(sa_column=Column("metadata", JSON))
    seo_title: dict = Field(sa_column=Column(JSON))
    seo_description: dict = Field(sa_column=Column(JSON))
    category_description: dict = Field(sa_column=Column(JSON))
    subcategories: list = Field(sa_column=Column(JSON))
    global_category_id: str
    global_category_parent_id: str
