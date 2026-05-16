import os

from sqlmodel import Session, create_engine

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5433/prep_scout",
)

engine = create_engine(DATABASE_URL)
