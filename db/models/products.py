from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.schema import UniqueConstraint

from db.models.base import Base


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[str]
    store: Mapped[str]
    name: Mapped[str]
    brand: Mapped[str]
    category: Mapped[str]
    unit: Mapped[str]
    comparative_unit: Mapped[str]
    price: Mapped[float]
    __table_args__ = (UniqueConstraint("external_id", "store"),)
