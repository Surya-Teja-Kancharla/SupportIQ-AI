from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config.settings import get_settings


settings = get_settings()

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autoflush=False,
    expire_on_commit=False,
)


def create_session() -> Session:
    """
    Create an independent SQLAlchemy session.

    Hour 14 uses this session for durable workflow execution
    telemetry so monitoring writes can commit independently
    of the main business transaction.
    """
    return SessionLocal()


def get_db_session():
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
