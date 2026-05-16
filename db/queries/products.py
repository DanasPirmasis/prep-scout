from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from db.models.products import Product


def get_by_external_id(
    session: Session, *, external_id: str, store: str
) -> Product | None:
    stmt = select(Product).where(
        Product.external_id == external_id, Product.store == store
    )
    return session.execute(stmt).scalar_one_or_none()


def upsert(
    session: Session,
    *,
    external_id: str,
    store: str,
    name: str,
    brand: str,
    category: str,
    unit: str,
    comparative_unit: str,
    price: float,
) -> Product:
    values = {
        "external_id": external_id,
        "store": store,
        "name": name,
        "brand": brand,
        "category": category,
        "unit": unit,
        "comparative_unit": comparative_unit,
        "price": price,
    }
    statement = (
        insert(Product)
        .values(**values)
        .on_conflict_do_update(
            index_elements=["external_id", "store"],
            set_={k: v for k, v in values.items() if k not in ("external_id", "store")},
        )
        .returning(Product)
    )
    return session.execute(statement).scalar_one()
