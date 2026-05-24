from sqlmodel import Session, col, select

from app.models.products import Product
from app.models.store import Store


def get_by_external_id(session: Session, *, external_id: str, store: Store) -> Product | None:
    stmt = select(Product).where(col(Product.external_id) == external_id, col(Product.store) == store)
    return session.exec(stmt).one_or_none()


def save_product(session: Session, product: Product) -> Product:
    session.add(product)
    session.commit()
    return product
