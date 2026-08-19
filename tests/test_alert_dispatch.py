"""AlertService dispatch — free tier no longer gets automatic alerts (2026-08-19)."""

import uuid
from datetime import UTC, datetime

import pytest

from sentinel_suisse.db.session import SessionLocal
from sentinel_suisse.models.enums import ChannelType, CountryCode, ListingType
from sentinel_suisse.models.listing import Listing
from sentinel_suisse.models.notification_channel import NotificationChannel
from sentinel_suisse.models.provider import Provider
from sentinel_suisse.models.saved_search import SavedSearch
from sentinel_suisse.models.user import User
from sentinel_suisse.notifications.base import AlertMessage, Notifier
from sentinel_suisse.security.pii import email_lookup, encrypt_pii
from sentinel_suisse.services.alerts import AlertService


class _RecordingNotifier(Notifier):
    def __init__(self) -> None:
        self.sent: list[AlertMessage] = []

    def send(self, message: AlertMessage) -> None:
        self.sent.append(message)


def _unique(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


@pytest.fixture
def db_session():
    from sentinel_suisse.config import get_settings

    get_settings.cache_clear()
    if not get_settings().database_url:
        pytest.skip("DATABASE_URL not configured in .env")
    session = SessionLocal()
    created_user_ids: list[int] = []
    session.info["created_user_ids"] = created_user_ids
    try:
        yield session
    finally:
        # dispatch_for_listing commits internally, so roll back what we can and
        # explicitly delete the rows we created to avoid poisoning future runs
        # (e.g. a saved search with no location filter matching every listing).
        if created_user_ids:
            from sentinel_suisse.models.user import User

            for user_id in created_user_ids:
                user = session.get(User, user_id)
                if user is not None:
                    session.delete(user)
            session.commit()
        session.close()


def _make_user(db_session, *, is_premium: bool, grandfathered: bool) -> User:
    email = f"{_unique('alert')}@example.com"
    user = User(
        email_lookup=email_lookup(email),
        email=encrypt_pii(email),
        is_active=True,
        is_premium=is_premium,
        free_alerts_grandfathered=grandfathered,
    )
    db_session.add(user)
    db_session.flush()
    db_session.info["created_user_ids"].append(user.id)
    return user


def _make_saved_search_and_channel(db_session, user: User, *, location: str) -> SavedSearch:
    now = datetime.now(UTC)
    channel = NotificationChannel(
        user_id=user.id,
        channel_type=ChannelType.EMAIL,
        channel_address=encrypt_pii("alerts@example.com"),
        is_verified=True,
        is_primary=True,
        verified_at=now,
        created_at=now,
    )
    db_session.add(channel)
    saved_search = SavedSearch(
        user_id=user.id,
        name="Emploi · Genève",
        query={"listing_type": "job", "location": location},
        is_active=True,
        created_at=now,
        updated_at=now,
    )
    db_session.add(saved_search)
    db_session.flush()
    return saved_search


def _make_listing(db_session, *, location: str) -> Listing:
    provider = Provider(
        name=_unique("Provider"),
        slug=_unique("provider"),
        base_url="https://example.com",
        is_active=True,
    )
    db_session.add(provider)
    db_session.flush()
    listing = Listing(
        provider_id=provider.id,
        external_id=_unique("ext"),
        listing_type=ListingType.JOB,
        title="Développeur",
        location=location,
        country=CountryCode.CH,
        source_url="https://example.com/job/1",
        content_hash=_unique("hash"),
        fetched_at=datetime.now(UTC),
    )
    db_session.add(listing)
    db_session.flush()
    return listing


def test_new_free_signup_does_not_receive_automatic_alerts(db_session) -> None:
    location = _unique("Geneve")
    user = _make_user(db_session, is_premium=False, grandfathered=False)
    _make_saved_search_and_channel(db_session, user, location=location)
    listing = _make_listing(db_session, location=location)
    db_session.commit()

    notifier = _RecordingNotifier()
    stats = AlertService(db_session, notifier=notifier).dispatch_for_listing(listing.id)

    assert stats.matched == 1
    assert stats.sent == 0
    assert stats.skipped == 1
    assert notifier.sent == []


def test_grandfathered_free_user_still_receives_alerts(db_session) -> None:
    location = _unique("Geneve")
    user = _make_user(db_session, is_premium=False, grandfathered=True)
    _make_saved_search_and_channel(db_session, user, location=location)
    listing = _make_listing(db_session, location=location)
    db_session.commit()

    notifier = _RecordingNotifier()
    stats = AlertService(db_session, notifier=notifier).dispatch_for_listing(listing.id)

    assert stats.sent == 1
    assert len(notifier.sent) == 1


def test_premium_user_receives_alerts_regardless_of_grandfather_flag(db_session) -> None:
    location = _unique("Geneve")
    user = _make_user(db_session, is_premium=True, grandfathered=False)
    _make_saved_search_and_channel(db_session, user, location=location)
    listing = _make_listing(db_session, location=location)
    db_session.commit()

    notifier = _RecordingNotifier()
    stats = AlertService(db_session, notifier=notifier).dispatch_for_listing(listing.id)

    assert stats.sent == 1
    assert len(notifier.sent) == 1
