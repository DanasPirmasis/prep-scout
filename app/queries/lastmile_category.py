from sqlmodel import Session

from app.models.lastmile_category import LastMileCategory


def get_by_id(session: Session, category_id: str) -> LastMileCategory | None:
    return session.get(LastMileCategory, category_id)
