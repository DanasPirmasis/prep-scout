from sqlmodel import Session, select

from app.models.lastmile_category import LastMileCategory


def get_by_id(session: Session, category_id: str) -> LastMileCategory | None:
    return session.exec(select(LastMileCategory).where(LastMileCategory.id == category_id)).one_or_none()


def save_category(session: Session, category: LastMileCategory) -> LastMileCategory:
    session.add(category)
    session.commit()
    return category
