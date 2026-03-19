import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from expense_tracker.models.expense import Base

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "expense_tracker")
DB_USER = os.getenv("DB_USER", "expense_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "expense_pass")
DB_PORT = os.getenv("DB_PORT", "5432")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def init_db():
    """Create all tables. Replaces init.sql."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """Dependency that provides a DB session and closes it when done."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
