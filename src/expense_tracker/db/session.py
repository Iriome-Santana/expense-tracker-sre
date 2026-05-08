import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from alembic.config import Config
from alembic import command

from expense_tracker.models.expense import Base

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "expense_tracker")
DB_USER = os.getenv("DB_USER", "expense_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "expense_pass")
DB_PORT = os.getenv("DB_PORT", "5432")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def run_migrations():
    """Ejecuta las migraciones pendientes al arrancar la app."""
    # Obtener la ruta absoluta del directorio raíz del proyecto
    # __file__ es session.py, subimos hasta la raíz del paquete instalado
    package_dir = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)
    )))
    alembic_ini = os.path.join(package_dir, "alembic.ini")
    migrations_dir = os.path.join(package_dir, "migrations")

    alembic_cfg = Config("/app/alembic.ini")
    alembic_cfg.set_main_option("script_location", "/app/migrations")
    command.upgrade(alembic_cfg, "head")


def init_db():
    """Mantener por compatibilidad. Las migraciones reemplazan create_all."""
    run_migrations()


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()