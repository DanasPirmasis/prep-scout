import json
from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import func
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, create_engine, select

from src.models.lastmile_category import LastMileCategory
from src.scraper.lastmile import save
from src.scraper.lastmile.types import LastMileCategoriesResponse

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CATEGORIES_FIXTURE = PROJECT_ROOT / "tests" / "fixtures" / "responses" / "lastmile-categories.json"


@pytest.fixture
def session() -> Iterator[Session]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    alembic_config = Config(str(PROJECT_ROOT / "alembic.ini"))

    with engine.begin() as connection:
        alembic_config.attributes["connection"] = connection
        command.upgrade(alembic_config, "head")

    with Session(engine) as session:
        yield session


def test_lastmile_categories_are_processed_and_saved(session: Session) -> None:
    response = LastMileCategoriesResponse.model_validate_json(CATEGORIES_FIXTURE.read_text())
    expected_category = response.data[0]

    print(response.count)
    save.categories(session, response)

    category_count = session.exec(select(func.count()).select_from(LastMileCategory)).one()
    category = session.get(LastMileCategory, expected_category.id)

    assert category_count == response.count
    assert category is not None
    assert category.name_lt == expected_category.name.lt
    assert category.name_en == expected_category.name.en
    assert category.name_ru == expected_category.name.ru
    assert category.parent_id == expected_category.parent_id
    assert category.icon_url == expected_category.icon_url
    assert category.global_category_parent_id == expected_category.global_category_parent_id
    assert category.date_last_refresh == str(expected_category.date_last_refresh)
    assert json.loads(category.store_ids) == expected_category.store_ids
    assert json.loads(category.slugs) == expected_category.slugs
    assert json.loads(category.mapping) == expected_category.mapping
    assert json.loads(category.metadata_) == expected_category.metadata
    assert json.loads(category.seo_title) == expected_category.seo_title
    assert json.loads(category.subcategories) == expected_category.subcategories

    save.categories(session, response)

    category_count_after_second_save = session.exec(select(func.count()).select_from(LastMileCategory)).one()
    assert category_count_after_second_save == response.count
