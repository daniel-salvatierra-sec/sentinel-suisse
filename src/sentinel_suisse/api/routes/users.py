"""User management routes (admin only)."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from sentinel_suisse.api.auth import verify_admin
from sentinel_suisse.api.deps import get_db
from sentinel_suisse.api.rate_limit import limiter
from sentinel_suisse.config import get_settings
from sentinel_suisse.models.user import User
from sentinel_suisse.schemas.user import UserCreate, UserCreated, UserRead, UserUpdate
from sentinel_suisse.security.tokens import generate_api_token, hash_api_token

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserRead])
@limiter.limit(lambda: get_settings().rate_limit)
def list_users(
    request: Request,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin),
) -> list[User]:
    return list(db.scalars(select(User).order_by(User.id)).all())


@router.get("/{user_id}", response_model=UserRead)
@limiter.limit(lambda: get_settings().rate_limit)
def get_user(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin),
) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post("", response_model=UserCreated, status_code=status.HTTP_201_CREATED)
@limiter.limit(lambda: get_settings().rate_limit)
def create_user(
    request: Request,
    payload: UserCreate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin),
) -> UserCreated:
    api_key = generate_api_token()
    user = User(
        email=str(payload.email).lower(),
        is_active=payload.is_active,
        api_token_hash=hash_api_token(api_key),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        ) from exc
    db.refresh(user)
    return UserCreated(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        created_at=user.created_at,
        api_key=api_key,
    )


@router.patch("/{user_id}", response_model=UserRead)
@limiter.limit(lambda: get_settings().rate_limit)
def update_user(
    request: Request,
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin),
) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    updates = payload.model_dump(exclude_unset=True)
    if "email" in updates and updates["email"] is not None:
        updates["email"] = str(updates["email"]).lower()

    for field, value in updates.items():
        setattr(user, field, value)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        ) from exc
    db.refresh(user)
    return user


@router.post("/{user_id}/regenerate-api-key", response_model=UserCreated)
@limiter.limit(lambda: get_settings().rate_limit)
def regenerate_api_key(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin),
) -> UserCreated:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    api_key = generate_api_token()
    user.api_token_hash = hash_api_token(api_key)
    db.commit()
    db.refresh(user)
    return UserCreated(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        created_at=user.created_at,
        api_key=api_key,
    )
