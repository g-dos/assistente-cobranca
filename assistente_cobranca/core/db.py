from __future__ import annotations

from sqlalchemy import create_engine, text
from collections.abc import Generator

from sqlalchemy.orm import Session, sessionmaker

from assistente_cobranca.core.config import settings
from assistente_cobranca.models.base import Base


engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("select 1"))
        return True
    except Exception:
        return False


def init_db() -> None:
    # importa models pra registrar no metadata
    import assistente_cobranca.models  # noqa: F401

    Base.metadata.create_all(bind=engine)

