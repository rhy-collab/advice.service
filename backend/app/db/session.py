import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from alembic import command
from alembic.config import Config


DEFAULT_DATABASE_URL = "sqlite:///./charter_law_dev.db"


class Base(DeclarativeBase):
    pass


def database_url() -> str:
    return os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


def engine_kwargs(url: str) -> dict[str, object]:
    if url.startswith("sqlite"):
        return {"connect_args": {"check_same_thread": False}}
    return {}


engine = create_engine(database_url(), **engine_kwargs(database_url()))
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def create_all_tables() -> None:
    import app.models.matter  # noqa: F401

    Base.metadata.create_all(bind=engine)


def run_migrations() -> None:
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", database_url())
    command.upgrade(config, "head")


def get_db() -> Generator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
