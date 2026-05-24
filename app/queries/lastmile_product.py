from sqlmodel import Session

from app.models.lastmile_product import LastMileProduct


def get_by_id(session: Session, product_id: str) -> LastMileProduct | None:
    return session.get(LastMileProduct, product_id)
