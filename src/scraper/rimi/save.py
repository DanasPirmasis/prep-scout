from sqlmodel import Session

from src.scraper.rimi.types import RimiCategoriesResponse


def categories(session: Session, data: RimiCategoriesResponse) -> None:
    pass
