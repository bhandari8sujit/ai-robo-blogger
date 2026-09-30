from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings


connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, echo=False, connect_args=connect_args)


def create_db_and_tables() -> None:
    # SQLModel reads all `table=True` classes from shared metadata to create missing tables.
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    # `yield` makes this a generator dependency: FastAPI cleans up the context after the response.
    with Session(engine) as session:
        yield session
