"""
Database connection and session lifecycle management for StockPilot.
Configured with SQLAlchemy 2.x and psycopg v3.
"""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from app.config import settings

# Configure SQLite-compatible arguments if running under test or SQLite URI
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

# SQLAlchemy 2.x Database Engine
# pool_pre_ping checks connection health before issuing queries to prevent stale connections
engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

# Session factory for generating scoped sessions per HTTP request
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)


class Base(DeclarativeBase):
    """
    SQLAlchemy 2.x Declarative Base class inherited by all ORM models.
    """
    pass


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a transactional database session per request
    and guarantees safe closure upon completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
