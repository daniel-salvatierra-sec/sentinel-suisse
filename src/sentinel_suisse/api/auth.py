"""Admin and user authentication."""

import secrets

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader, HTTPBasic, HTTPBasicCredentials
from sqlalchemy import select
from sqlalchemy.orm import Session

from sentinel_suisse.api.deps import get_db
from sentinel_suisse.config import get_settings
from sentinel_suisse.models.user import User
from sentinel_suisse.security.tokens import verify_api_token

security = HTTPBasic()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_admin(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    settings = get_settings()
    if not settings.admin_username or not settings.admin_password_hash:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin authentication is not configured",
        )

    username_ok = secrets.compare_digest(
        credentials.username.encode("utf-8"),
        settings.admin_username.encode("utf-8"),
    )
    password_ok = bcrypt.checkpw(
        credentials.password.encode("utf-8"),
        settings.admin_password_hash.encode("utf-8"),
    )

    if not (username_ok and password_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username


def get_current_user(
    x_api_key: str | None = Depends(api_key_header),
    db: Session = Depends(get_db),
) -> User:
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key header",
        )

    x_api_key = x_api_key.strip()
    stmt = select(User).where(User.is_active.is_(True), User.api_token_hash.isnot(None))
    for user in db.scalars(stmt):
        if user.api_token_hash and verify_api_token(x_api_key, user.api_token_hash):
            return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key",
    )


def verify_admin_or_user(
    credentials: HTTPBasicCredentials | None = Depends(HTTPBasic(auto_error=False)),
    x_api_key: str | None = Depends(api_key_header),
    db: Session = Depends(get_db),
) -> str:
    """Allow admin (HTTP Basic) or application user (X-API-Key) for read-only search."""
    if x_api_key:
        get_current_user(x_api_key=x_api_key, db=db)
        return "user"

    if credentials is not None:
        return verify_admin(credentials)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Provide X-API-Key or admin HTTP Basic credentials",
        headers={"WWW-Authenticate": "Basic"},
    )
