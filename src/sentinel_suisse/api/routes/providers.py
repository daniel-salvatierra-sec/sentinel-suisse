"""Provider CRUD routes (admin only)."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from sentinel_suisse.api.auth import verify_admin
from sentinel_suisse.api.deps import get_db
from sentinel_suisse.api.rate_limit import limiter
from sentinel_suisse.config import get_settings
from sentinel_suisse.models.provider import Provider
from sentinel_suisse.schemas.provider import ProviderCreate, ProviderRead, ProviderUpdate

router = APIRouter(prefix="/providers", tags=["providers"])


@router.get("", response_model=list[ProviderRead])
@limiter.limit(lambda: get_settings().rate_limit)
def list_providers(
    request: Request,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin),
) -> list[Provider]:
    return list(db.scalars(select(Provider).order_by(Provider.id)).all())


@router.get("/{provider_id}", response_model=ProviderRead)
@limiter.limit(lambda: get_settings().rate_limit)
def get_provider(
    request: Request,
    provider_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin),
) -> Provider:
    provider = db.get(Provider, provider_id)
    if provider is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found")
    return provider


@router.post("", response_model=ProviderRead, status_code=status.HTTP_201_CREATED)
@limiter.limit(lambda: get_settings().rate_limit)
def create_provider(
    request: Request,
    payload: ProviderCreate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin),
) -> Provider:
    provider = Provider(
        name=payload.name,
        slug=payload.slug,
        base_url=str(payload.base_url),
        is_active=payload.is_active,
    )
    db.add(provider)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Provider with this name or slug already exists",
        ) from exc
    db.refresh(provider)
    return provider


@router.patch("/{provider_id}", response_model=ProviderRead)
@limiter.limit(lambda: get_settings().rate_limit)
def update_provider(
    request: Request,
    provider_id: int,
    payload: ProviderUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin),
) -> Provider:
    provider = db.get(Provider, provider_id)
    if provider is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found")

    updates = payload.model_dump(exclude_unset=True)
    if "base_url" in updates and updates["base_url"] is not None:
        updates["base_url"] = str(updates["base_url"])

    for field, value in updates.items():
        setattr(provider, field, value)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Provider with this name or slug already exists",
        ) from exc
    db.refresh(provider)
    return provider


@router.delete("/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(lambda: get_settings().rate_limit)
def delete_provider(
    request: Request,
    provider_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin),
) -> None:
    provider = db.get(Provider, provider_id)
    if provider is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found")
    db.delete(provider)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete provider with existing listings",
        ) from exc
