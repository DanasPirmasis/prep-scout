from sqlmodel import Session, select

from app.models.lastmile_product import LastMileProduct


def get_by_id(session: Session, product_id: str) -> LastMileProduct | None:
    return session.exec(select(LastMileProduct).where(LastMileProduct.id == product_id)).one_or_none()


def save_product(session: Session, product: LastMileProduct) -> LastMileProduct:
    session.add(product)
    session.commit()
    session.refresh(product)
    return product
