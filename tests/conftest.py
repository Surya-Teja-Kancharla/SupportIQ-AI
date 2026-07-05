import os
from pathlib import Path
from uuid import uuid4

import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.database.base import Base


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(dotenv_path=ENV_FILE, override=True)


def build_test_database_url() -> str:
    database_url = os.environ.get("TEST_DATABASE_URL")

    if not database_url:
        pytest.fail(
            f"TEST_DATABASE_URL is not configured. "
            f"Expected .env file: {ENV_FILE}"
        )

    url = make_url(database_url)

    if url.get_backend_name() != "postgresql":
        pytest.fail(
            "TEST_DATABASE_URL must reference PostgreSQL."
        )

    database_name = url.database or ""

    if "test" not in database_name.lower():
        pytest.fail(
            "Refusing to run tests against a database whose "
            "name does not contain 'test'."
        )

    return database_url


@pytest.fixture(scope="session")
def test_engine():
    database_url = build_test_database_url()

    engine = create_engine(
        database_url,
        pool_pre_ping=True,
    )

    Base.metadata.create_all(engine)

    yield engine

    engine.dispose()


@pytest.fixture
def db_session(test_engine):
    connection = test_engine.connect()
    transaction = connection.begin()

    session = Session(
        bind=connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )

    try:
        yield session
    finally:
        session.close()

        if transaction.is_active:
            transaction.rollback()

        connection.close()


@pytest.fixture
def unique_suffix():
    return uuid4().hex
