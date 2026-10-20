import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import BaseModel
from app.models import Customer, SalesOrder  # noqa: F401


@pytest.fixture
def test_session() -> Session:
    test_engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    BaseModel.metadata.create_all(test_engine)
    test_session_factory = sessionmaker(bind=test_engine, expire_on_commit=False)
    with test_session_factory() as session:
        yield session
    BaseModel.metadata.drop_all(test_engine)
    test_engine.dispose()
