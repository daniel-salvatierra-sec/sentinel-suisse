"""Operator insights: boosts, signups, Stripe revenue, multi-app hub."""

from __future__ import annotations

import json
import logging
from collections import defaultdict
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from typing import Any

import stripe
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from sentinel_suisse.config import Settings
from sentinel_suisse.models.listing import Listing
from sentinel_suisse.models.user import User
from sentinel_suisse.schemas.admin_dashboard import (
    ActiveBoostRow,
    AdminInsights,
    DailySignupMetric,
    OpsAppCard,
    RecentPaymentRow,
    StripeRevenueSummary,
    WeeklyPaymentMetric,
)
from sentinel_suisse.services.sponsor_ads import sponsor_revenue_summary

logger = logging.getLogger(__name__)


def _week_start(day: date) -> date:
    return day - timedelta(days=day.weekday())


def list_active_boosts(db: Session, *, limit: int = 50) -> list[ActiveBoostRow]:
    now = datetime.now(UTC)
    rows = db.scalars(
        select(Listing)
        .where(
            Listing.is_featured.is_(True),
            or_(Listing.featured_until.is_(None), Listing.featured_until > now),
        )
        .order_by(Listing.featured_until.asc().nulls_last(), Listing.id.desc())
        .limit(limit)
    ).all()
    return [
        ActiveBoostRow(
            id=row.id,
            title=row.title,
            listing_type=row.listing_type,
            location=row.location,
            owner_user_id=row.owner_user_id,
            featured_until=row.featured_until,
        )
        for row in rows
    ]


def signup_metrics(db: Session, *, days: int = 14) -> list[DailySignupMetric]:
    cutoff = datetime.now(UTC) - timedelta(days=max(1, days) - 1)
    day_col = func.date(User.created_at)
    grouped = db.execute(
        select(day_col.label("day"), func.count())
        .where(User.created_at >= cutoff)
        .group_by(day_col)
        .order_by(day_col)
    ).all()
    counts = {row.day: int(row[1]) for row in grouped}

    start = cutoff.date()
    end = datetime.now(UTC).date()
    out: list[DailySignupMetric] = []
    cursor = start
    while cursor <= end:
        out.append(DailySignupMetric(day=cursor, count=counts.get(cursor, 0)))
        cursor += timedelta(days=1)
    return out


def _payment_kind(session_obj: dict[str, Any]) -> str:
    metadata = session_obj.get("metadata") or {}
    purpose = metadata.get("purpose")
    if purpose == "feature_listing":
        return "boost"
    if purpose == "sponsor_ad":
        return "sponsor"
    if session_obj.get("mode") == "subscription":
        return "premium"
    return "other"


def _amount_chf(session_obj: dict[str, Any]) -> Decimal:
    total = session_obj.get("amount_total")
    if total is None:
        return Decimal("0")
    return (Decimal(str(total)) / Decimal("100")).quantize(Decimal("0.01"))


def stripe_revenue_summary(settings: Settings, *, days: int = 90) -> StripeRevenueSummary:
    empty = StripeRevenueSummary(
        configured=False,
        currency="chf",
        last_30_days_total_chf=Decimal("0"),
        premium_payments_30d=0,
        boost_payments_30d=0,
        sponsor_payments_30d=0,
        recent_payments=[],
        payments_by_week=[],
    )
    if not settings.stripe_secret_key:
        return empty

    stripe.api_key = settings.stripe_secret_key
    since = int((datetime.now(UTC) - timedelta(days=days)).timestamp())
    since_30 = datetime.now(UTC) - timedelta(days=30)

    events: list[dict[str, Any]] = []
    try:
        page = stripe.checkout.Session.list(
            status="complete",
            created={"gte": since},
            limit=100,
        )
        for session in page.auto_paging_iter():
            created_ts = session.get("created")
            if created_ts is None:
                continue
            events.append(
                {
                    "id": str(session.get("id") or ""),
                    "created": datetime.fromtimestamp(int(created_ts), tz=UTC),
                    "amount_total": session.get("amount_total"),
                    "currency": (session.get("currency") or "chf").lower(),
                    "mode": session.get("mode"),
                    "metadata": dict(session.get("metadata") or {}),
                }
            )
    except stripe.StripeError:
        logger.exception("admin stripe checkout list failed")
        return empty

    currency = "chf"
    if events:
        currency = str(events[0].get("currency") or "chf").lower()

    premium_30 = 0
    boost_30 = 0
    sponsor_30 = 0
    total_30 = Decimal("0")
    weekly: dict[date, dict[str, Any]] = defaultdict(
        lambda: {"premium": 0, "boost": 0, "sponsor": 0, "amount": Decimal("0")}
    )

    recent: list[RecentPaymentRow] = []
    for event in sorted(events, key=lambda item: item["created"], reverse=True):
        kind = _payment_kind(event)
        amount = _amount_chf(event)
        week = _week_start(event["created"].date())
        weekly[week]["amount"] += amount
        if kind == "premium":
            weekly[week]["premium"] += 1
        elif kind == "boost":
            weekly[week]["boost"] += 1
        elif kind == "sponsor":
            weekly[week]["sponsor"] += 1

        if event["created"] >= since_30:
            total_30 += amount
            if kind == "premium":
                premium_30 += 1
            elif kind == "boost":
                boost_30 += 1
            elif kind == "sponsor":
                sponsor_30 += 1

        if len(recent) < 15:
            label = "Boost anuncio"
            if kind == "premium":
                label = "Premium"
            elif kind == "sponsor":
                label = "Patrocinio"
            elif kind == "other":
                label = "Otro pago"
            metadata = event.get("metadata") or {}
            listing_id_raw = metadata.get("listing_id")
            listing_id = int(listing_id_raw) if listing_id_raw else None
            sponsor_id_raw = metadata.get("sponsor_id")
            sponsor_id = int(sponsor_id_raw) if sponsor_id_raw else None
            recent.append(
                RecentPaymentRow(
                    checkout_id=event["id"],
                    kind=kind,
                    label=label,
                    amount_chf=amount,
                    paid_at=event["created"],
                    listing_id=listing_id,
                    sponsor_id=sponsor_id,
                )
            )

    payments_by_week = [
        WeeklyPaymentMetric(
            week_start=week,
            premium_count=bucket["premium"],
            boost_count=bucket["boost"],
            sponsor_count=bucket["sponsor"],
            amount_chf=bucket["amount"].quantize(Decimal("0.01")),
        )
        for week, bucket in sorted(weekly.items(), reverse=True)
    ][:12]

    return StripeRevenueSummary(
        configured=True,
        currency=currency,
        last_30_days_total_chf=total_30.quantize(Decimal("0.01")),
        premium_payments_30d=premium_30,
        boost_payments_30d=boost_30,
        sponsor_payments_30d=sponsor_30,
        recent_payments=recent,
        payments_by_week=payments_by_week,
    )


def ops_app_cards(settings: Settings) -> list[OpsAppCard]:
    base = settings.public_app_url.rstrip("/")
    current = OpsAppCard(
        id="linkswiss",
        name="LinkSwiss",
        public_url=base,
        admin_url=f"{base}/admin",
        status="live",
        is_current=True,
    )
    raw = (settings.ops_apps_json or "").strip()
    if not raw:
        return [current]

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("invalid OPS_APPS_JSON")
        return [current]

    if not isinstance(payload, list):
        return [current]

    cards: list[OpsAppCard] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        app_id = str(item.get("id") or "").strip()
        name = str(item.get("name") or app_id or "App").strip()
        public_url = str(item.get("public_url") or "").strip().rstrip("/")
        if not app_id or not public_url:
            continue
        admin_path = str(item.get("admin_path") or "/admin").strip()
        if not admin_path.startswith("/"):
            admin_path = f"/{admin_path}"
        admin_url = str(item.get("admin_url") or f"{public_url}{admin_path}").strip()
        status = str(item.get("status") or "live").strip()
        is_current = app_id == "linkswiss" or public_url == base
        cards.append(
            OpsAppCard(
                id=app_id,
                name=name,
                public_url=public_url,
                admin_url=admin_url,
                status=status,
                is_current=is_current,
            )
        )

    if not any(card.is_current for card in cards):
        cards.insert(0, current)
    return cards or [current]


def admin_insights(db: Session, settings: Settings) -> AdminInsights:
    stripe_summary = stripe_revenue_summary(settings)
    return AdminInsights(
        apps=ops_app_cards(settings),
        active_boosts=list_active_boosts(db),
        signups_by_day=signup_metrics(db),
        stripe=stripe_summary,
        sponsors=sponsor_revenue_summary(db),
    )
