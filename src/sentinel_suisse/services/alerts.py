"""Alert dispatch and audit logging."""

from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from sentinel_suisse.models.alert_log import AlertLog
from sentinel_suisse.models.enums import AlertStatus
from sentinel_suisse.models.listing import Listing
from sentinel_suisse.models.notification_channel import NotificationChannel
from sentinel_suisse.models.saved_search import SavedSearch
from sentinel_suisse.notifications.base import AlertMessage, Notifier
from sentinel_suisse.notifications.factory import get_notifier_for_channel
from sentinel_suisse.schemas.search import SearchQuery
from sentinel_suisse.services.matching import listing_matches_query


@dataclass
class DispatchStats:
    matched: int = 0
    sent: int = 0
    skipped: int = 0
    failed: int = 0


class AlertService:
    def __init__(self, db: Session, notifier: Notifier | None = None) -> None:
        self.db = db
        self._override_notifier = notifier

    def dispatch_for_listing(self, listing_id: int) -> DispatchStats:
        listing = self.db.get(Listing, listing_id)
        if listing is None:
            msg = f"Listing not found: {listing_id}"
            raise ValueError(msg)

        stats = DispatchStats()
        saved_searches = self.db.scalars(
            select(SavedSearch).where(SavedSearch.is_active.is_(True))
        ).all()

        for saved_search in saved_searches:
            filters = SearchQuery.model_validate(saved_search.query)
            if not listing_matches_query(listing, filters):
                continue

            stats.matched += 1
            channel = self._primary_verified_channel(saved_search.user_id)
            if channel is None:
                stats.failed += 1
                continue

            if self._already_alerted(saved_search, listing):
                stats.skipped += 1
                continue

            alert = self._record_alert(
                saved_search,
                listing,
                channel_type=channel.channel_type.value,
                status=AlertStatus.PENDING,
            )
            try:
                alert_message = AlertMessage(
                    listing=listing,
                    saved_search=saved_search,
                    channel_address=channel.channel_address,
                    channel_type=channel.channel_type.value,
                )
                notifier = (
                    self._override_notifier
                    if self._override_notifier is not None
                    else get_notifier_for_channel(channel.channel_type)
                )
                notifier.send(alert_message)
                alert.status = AlertStatus.SENT
                alert.sent_at = datetime.now(UTC)
                stats.sent += 1
            except Exception as exc:  # noqa: BLE001 — delivery backends may raise varied errors
                alert.status = AlertStatus.FAILED
                alert.error_message = str(exc)[:1000]
                stats.failed += 1

        self.db.commit()
        return stats

    def _primary_verified_channel(self, user_id: int) -> NotificationChannel | None:
        stmt = (
            select(NotificationChannel)
            .where(
                NotificationChannel.user_id == user_id,
                NotificationChannel.is_verified.is_(True),
            )
            .order_by(NotificationChannel.is_primary.desc(), NotificationChannel.id)
        )
        return self.db.scalar(stmt)

    def _already_alerted(self, saved_search: SavedSearch, listing: Listing) -> bool:
        existing = self.db.scalar(
            select(AlertLog.id).where(
                AlertLog.user_id == saved_search.user_id,
                AlertLog.saved_search_id == saved_search.id,
                AlertLog.listing_id == listing.id,
            )
        )
        return existing is not None

    def _record_alert(
        self,
        saved_search: SavedSearch,
        listing: Listing,
        *,
        channel_type: str,
        status: AlertStatus,
        error_message: str | None = None,
    ) -> AlertLog:
        alert = AlertLog(
            user_id=saved_search.user_id,
            saved_search_id=saved_search.id,
            listing_id=listing.id,
            channel_type=channel_type,
            status=status,
            error_message=error_message,
            created_at=datetime.now(UTC),
        )
        self.db.add(alert)
        self.db.flush()
        return alert
