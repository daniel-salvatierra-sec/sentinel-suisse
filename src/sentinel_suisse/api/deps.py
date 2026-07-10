"""Shared API dependencies."""

from collections.abc import Generator

from sqlalchemy.orm import Session

from sentinel_suisse.db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
