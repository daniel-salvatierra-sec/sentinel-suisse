"""Saved search routes (user-scoped via X-API-Key)."""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from sentinel_suisse.api.auth import get_current_user
from sentinel_suisse.api.deps import get_db
from sentinel_suisse.api.rate_limit import limiter
from sentinel_suisse.config import get_settings
from sentinel_suisse.models.saved_search import SavedSearch
from sentinel_suisse.models.user import User
from sentinel_suisse.schemas.saved_search import (
    SavedSearchCreate,
    SavedSearchRead,
    SavedSearchUpdate,
)

router = APIRouter(prefix="/saved-searches", tags=["saved-searches"])


@router.get("", response_model=list[SavedSearchRead])
@limiter.limit(lambda: get_settings().rate_limit)
def list_saved_searches(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SavedSearch]:
    stmt = (
        select(SavedSearch).where(SavedSearch.user_id == current_user.id).order_by(SavedSearch.id)
    )
    return list(db.scalars(stmt).all())


@router.get("/{saved_search_id}", response_model=SavedSearchRead)
@limiter.limit(lambda: get_settings().rate_limit)
def get_saved_search(
    request: Request,
    saved_search_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SavedSearch:
    saved_search = _get_owned_search(db, current_user, saved_search_id)
    return saved_search


@router.post("", response_model=SavedSearchRead, status_code=status.HTTP_201_CREATED)
@limiter.limit(lambda: get_settings().rate_limit)
def create_saved_search(
    request: Request,
    payload: SavedSearchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SavedSearch:
    now = datetime.now(UTC)
    saved_search = SavedSearch(
        user_id=current_user.id,
        name=payload.name,
        query=payload.query.model_dump(mode="json", exclude_none=True),
        is_active=payload.is_active,
        created_at=now,
        updated_at=now,
    )
    db.add(saved_search)
    db.commit()
    db.refresh(saved_search)
    return saved_search


@router.patch("/{saved_search_id}", response_model=SavedSearchRead)
@limiter.limit(lambda: get_settings().rate_limit)
def update_saved_search(
    request: Request,
    saved_search_id: int,
    payload: SavedSearchUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SavedSearch:
    saved_search = _get_owned_search(db, current_user, saved_search_id)

    updates = payload.model_dump(exclude_unset=True, mode="json")

    for field, value in updates.items():
        setattr(saved_search, field, value)

    db.commit()
    db.refresh(saved_search)
    return saved_search


@router.delete("/{saved_search_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(lambda: get_settings().rate_limit)
def delete_saved_search(
    request: Request,
    saved_search_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    saved_search = _get_owned_search(db, current_user, saved_search_id)
    db.delete(saved_search)
    db.commit()


def _get_owned_search(db: Session, user: User, saved_search_id: int) -> SavedSearch:
    saved_search = db.get(SavedSearch, saved_search_id)
    if saved_search is None or saved_search.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved search not found")
    return saved_search
