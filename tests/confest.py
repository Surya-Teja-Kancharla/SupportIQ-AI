import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database.base import Base


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
    )

    Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

        session.rollback()

    Base.metadata.drop_all(engine)
    engine.dispose()
