from typing import ClassVar

from sqlmodel import Field, SQLModel


class RimiProduct(SQLModel, table=True):
    __tablename__: ClassVar[str] = "rimi_products"  # type: ignore[override]

    id: str = Field(primary_key=True)
    name: str
    category: str
    brand: str | None = None
    price: float
    currency: str
    url: str
    image_url: str | None = None
    price_text: str | None = None
    unit_price_text: str | None = None
    comparative_unit: str | None = None
    data_gtm_eec_product: str
