import os
from collections.abc import Generator
from contextlib import contextmanager

from sqlmodel import Session, create_engine

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5433/prep_scout",
)

engine = create_engine(DATABASE_URL)


@contextmanager
def session_scope() -> Generator[Session]:
    with Session(engine) as session:
        yield session
