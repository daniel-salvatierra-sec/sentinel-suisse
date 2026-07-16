"""Health checks for load balancers and monitoring."""

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from sentinel_suisse.config import get_settings


def check_database(engine: Engine | None = None) -> bool:
    """Return True when the database accepts a simple query."""
    owned = engine is None
    if owned:
        engine = create_engine(get_settings().database_url, pool_pre_ping=True)
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
    finally:
        if owned:
            engine.dispose()
