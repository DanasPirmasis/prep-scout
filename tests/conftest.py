from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, create_engine

PROJECT_ROOT = Path(__file__).resolve().parents[1]


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
