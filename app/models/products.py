from typing import ClassVar

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class Product(SQLModel, table=True):
    __tablename__: ClassVar[str] = "products"  # type: ignore[override]
    __table_args__: ClassVar[tuple] = (UniqueConstraint("external_id", "store"),)  # type: ignore[override]

    id: int | None = Field(default=None, primary_key=True)
    external_id: str
    store: str
    name: str
    brand: str
    category: str
    unit: str
    comparative_unit: str
    price: float
