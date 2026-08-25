"""Operator cockpit queries (counts, ingest freshness, listing hide)."""

import logging
from datetime import UTC, datetime

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from sentinel_suisse.config import get_settings
from sentinel_suisse.models.enums import ListingType
from sentinel_suisse.models.listing import Listing
from sentinel_suisse.models.provider import Provider
from sentinel_suisse.models.user import User
from sentinel_suisse.schemas.admin_dashboard import (
    AdminListingRow,
    DashboardOverview,
    ProviderIngestHealth,
)
from sentinel_suisse.schemas.user import UserRead, to_user_read
from sentinel_suisse.services.entitlements import count_saved_searches
from sentinel_suisse.services.health import check_database
from sentinel_suisse.services.listing_freshness import freshness_cutoff

logger = logging.getLogger(__name__)


def dashboard_overview(db: Session) -> DashboardOverview:
    settings = get_settings()
    cutoff = freshness_cutoff()
    now = datetime.now(UTC)

    users_total = int(db.scalar(select(func.count()).select_from(User)) or 0)
    users_active = int(
        db.scalar(select(func.count()).select_from(User).where(User.is_active.is_(True))) or 0
    )
    users_premium = int(
        db.scalar(select(func.count()).select_from(User).where(User.is_premium.is_(True))) or 0
    )

    listings_housing = int(
        db.scalar(
            select(func.count())
            .select_from(Listing)
            .where(Listing.listing_type == ListingType.HOUSING)
        )
        or 0
    )
    listings_job = int(
        db.scalar(
            select(func.count()).select_from(Listing).where(Listing.listing_type == ListingType.JOB)
        )
        or 0
    )
    listings_direct = int(
        db.scalar(
            select(func.count()).select_from(Listing).where(Listing.owner_user_id.is_not(None))
        )
        or 0
    )
    listings_hidden = int(
        db.scalar(select(func.count()).select_from(Listing).where(Listing.is_hidden.is_(True))) or 0
    )

    provider_rows = db.execute(
        select(
            Provider.slug,
            Provider.name,
            Provider.is_active,
            func.count(Listing.id),
            func.max(Listing.fetched_at),
        )
        .outerjoin(Listing, Listing.provider_id == Provider.id)
        .group_by(Provider.id, Provider.slug, Provider.name, Provider.is_active)
        .order_by(Provider.slug)
    ).all()

    providers: list[ProviderIngestHealth] = []
    for slug, name, is_active, listing_count, last_fetched in provider_rows:
        hours_since: float | None = None
        if last_fetched is not None:
            hours_since = round((now - last_fetched).total_seconds() / 3600, 1)
        is_direct = slug == "direct"
        stale = False
        if is_active and not is_direct:
            if last_fetched is None:
                stale = True
            elif cutoff is not None and last_fetched < cutoff:
                stale = True
        providers.append(
            ProviderIngestHealth(
                slug=slug,
                name=name,
                is_active=is_active,
                listing_count=int(listing_count or 0),
                last_fetched_at=last_fetched,
                hours_since_fetch=hours_since,
                stale=stale,
            )
        )

    return DashboardOverview(
        users_total=users_total,
        users_active=users_active,
        users_premium=users_premium,
        listings_housing=listings_housing,
        listings_job=listings_job,
        listings_direct=listings_direct,
        listings_hidden=listings_hidden,
        listing_fresh_hours=settings.listing_fresh_hours,
        database_ok=check_database(),
        providers=providers,
    )


def listing_to_row(listing: Listing, provider_slug: str) -> AdminListingRow:
    return AdminListingRow(
        id=listing.id,
        title=listing.title,
        listing_type=listing.listing_type,
        location=listing.location,
        source_url=listing.source_url,
        fetched_at=listing.fetched_at,
        is_hidden=listing.is_hidden,
        owner_user_id=listing.owner_user_id,
        provider_slug=provider_slug,
        description=listing.description,
        price=listing.price,
    )


def list_admin_listings(
    db: Session,
    *,
    q: str | None = None,
    listing_type: ListingType | None = None,
    hidden: bool | None = None,
    owner_only: bool = False,
    limit: int = 50,
) -> list[AdminListingRow]:
    stmt = (
        select(Listing, Provider.slug)
        .join(Provider, Listing.provider_id == Provider.id)
        .order_by(Listing.id.desc())
        .limit(limit)
    )
    if q:
        needle = f"%{q.strip()}%"
        stmt = stmt.where(
            or_(
                Listing.title.ilike(needle),
                Listing.location.ilike(needle),
                Listing.external_id.ilike(needle),
            )
        )
    if listing_type is not None:
        stmt = stmt.where(Listing.listing_type == listing_type)
    if hidden is not None:
        stmt = stmt.where(Listing.is_hidden.is_(hidden))
    if owner_only:
        stmt = stmt.where(Listing.owner_user_id.is_not(None))

    rows = db.execute(stmt).all()
    return [listing_to_row(listing, slug) for listing, slug in rows]


def set_listing_hidden(db: Session, listing: Listing, is_hidden: bool) -> Listing:
    listing.is_hidden = is_hidden
    db.commit()
    db.refresh(listing)
    return listing


def list_recent_users(db: Session, *, limit: int = 50) -> list[User]:
    return list(
        db.scalars(select(User).order_by(User.created_at.desc(), User.id.desc()).limit(limit)).all()
    )


def user_row(db: Session, user: User) -> UserRead:
    return to_user_read(user, saved_search_count=count_saved_searches(db, user))


def set_user_free_alerts(db: Session, user: User, *, free_alerts_grandfathered: bool) -> User:
    user.free_alerts_grandfathered = free_alerts_grandfathered
    db.commit()
    db.refresh(user)
    return user


def readable_user_rows(db: Session, *, limit: int = 50) -> list[UserRead]:
    rows: list[UserRead] = []
    for user in list_recent_users(db, limit=limit):
        try:
            rows.append(user_row(db, user))
        except ValueError:
            logger.warning("Skipping user id=%s with undecryptable email", user.id)
    return rows
