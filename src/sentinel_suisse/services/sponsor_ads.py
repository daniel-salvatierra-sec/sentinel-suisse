"""Manual sponsor placements for Phase 1 advertising."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from sentinel_suisse.models.sponsor_ad import SponsorAd
from sentinel_suisse.schemas.sponsor_ad import (
    SponsorAdAdminRow,
    SponsorAdCreate,
    SponsorAdPublic,
    SponsorAdUpdate,
    SponsorRevenueSummary,
)


def _now() -> datetime:
    return datetime.now(UTC)


def _is_live(row: SponsorAd, *, at: datetime | None = None) -> bool:
    if not row.is_active:
        return False
    moment = at or _now()
    if row.starts_at is not None and row.starts_at > moment:
        return False
    if row.ends_at is not None and row.ends_at <= moment:
        return False
    return True


def list_admin_sponsors(db: Session, *, limit: int = 100) -> list[SponsorAdAdminRow]:
    rows = db.scalars(
        select(SponsorAd).order_by(SponsorAd.sort_order.asc(), SponsorAd.id.desc()).limit(limit)
    ).all()
    return [SponsorAdAdminRow.model_validate(row) for row in rows]


def list_public_sponsors(
    db: Session,
    *,
    context: str = "all",
    placement: str = "banner",
    limit: int = 3,
) -> list[SponsorAdPublic]:
    moment = _now()
    stmt = (
        select(SponsorAd)
        .where(
            SponsorAd.is_active.is_(True),
            SponsorAd.placement == placement,
            or_(SponsorAd.starts_at.is_(None), SponsorAd.starts_at <= moment),
            or_(SponsorAd.ends_at.is_(None), SponsorAd.ends_at > moment),
        )
        .order_by(SponsorAd.sort_order.asc(), SponsorAd.id.desc())
        .limit(limit)
    )
    if context in {"housing", "job"}:
        stmt = stmt.where(or_(SponsorAd.context == "all", SponsorAd.context == context))
    rows = db.scalars(stmt).all()
    return [
        SponsorAdPublic(
            id=row.id,
            placement=row.placement,
            headline=row.headline,
            image_url=row.image_url,
            target_url=row.target_url,
        )
        for row in rows
    ]


def create_sponsor(db: Session, payload: SponsorAdCreate) -> SponsorAdAdminRow:
    row = SponsorAd(
        sponsor_name=payload.sponsor_name.strip(),
        placement=payload.placement,
        context=payload.context,
        headline=payload.headline.strip() if payload.headline else None,
        image_url=str(payload.image_url) if payload.image_url else None,
        target_url=str(payload.target_url),
        monthly_chf=payload.monthly_chf,
        starts_at=payload.starts_at,
        ends_at=payload.ends_at,
        is_active=payload.is_active,
        sort_order=payload.sort_order,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return SponsorAdAdminRow.model_validate(row)


def update_sponsor(db: Session, row: SponsorAd, payload: SponsorAdUpdate) -> SponsorAdAdminRow:
    data = payload.model_dump(exclude_unset=True)
    if "sponsor_name" in data and data["sponsor_name"] is not None:
        data["sponsor_name"] = data["sponsor_name"].strip()
    if "headline" in data and data["headline"] is not None:
        data["headline"] = data["headline"].strip() or None
    if "image_url" in data and data["image_url"] is not None:
        data["image_url"] = str(data["image_url"])
    if "target_url" in data and data["target_url"] is not None:
        data["target_url"] = str(data["target_url"])

    for key, value in data.items():
        setattr(row, key, value)

    if not row.headline and not row.image_url:
        msg = "headline or image_url is required"
        raise ValueError(msg)
    if row.starts_at and row.ends_at and row.starts_at > row.ends_at:
        msg = "starts_at cannot be after ends_at"
        raise ValueError(msg)

    db.commit()
    db.refresh(row)
    return SponsorAdAdminRow.model_validate(row)


def delete_sponsor(db: Session, row: SponsorAd) -> None:
    db.delete(row)
    db.commit()


def record_sponsor_event(db: Session, sponsor_id: int, *, kind: str) -> bool:
    row = db.get(SponsorAd, sponsor_id)
    if row is None or not row.is_active:
        return False
    if kind == "click":
        row.click_count += 1
    else:
        row.impression_count += 1
    db.commit()
    return True


def sponsor_revenue_summary(db: Session) -> SponsorRevenueSummary:
    rows = db.scalars(
        select(SponsorAd).order_by(SponsorAd.sort_order.asc(), SponsorAd.id.desc())
    ).all()
    active_rows = [row for row in rows if _is_live(row)]
    active_admin = [SponsorAdAdminRow.model_validate(row) for row in active_rows]
    estimated = sum((row.monthly_chf for row in active_rows), Decimal("0")).quantize(
        Decimal("0.01")
    )
    impressions = sum(int(row.impression_count) for row in rows)
    clicks = sum(int(row.click_count) for row in rows)
    return SponsorRevenueSummary(
        active_count=len(active_rows),
        estimated_monthly_chf=estimated,
        total_impressions=impressions,
        total_clicks=clicks,
        active_sponsors=active_admin,
    )
