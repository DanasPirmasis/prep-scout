from datetime import datetime
from typing import ClassVar

from sqlmodel import Field, SQLModel


class PriceHistory(SQLModel, table=True):
    __tablename__: ClassVar[str] = "price_history"  # type: ignore[override]

    id: int | None = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="products.id")
    price: float
    retail_price: float | None = None
    special_price: float | None = None
    is_available: bool
    created_at: datetime
