"""Public alert subscription — user + channels + saved search in one transaction."""

from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from sentinel_suisse.models.enums import ChannelType
from sentinel_suisse.models.notification_channel import NotificationChannel
from sentinel_suisse.models.saved_search import SavedSearch
from sentinel_suisse.models.user import User
from sentinel_suisse.schemas.public_signup import PublicAlertSignup
from sentinel_suisse.security.pii import email_lookup, encrypt_pii
from sentinel_suisse.security.tokens import generate_api_token, hash_api_token


@dataclass
class PublicSignupResult:
    user: User
    api_key: str
    saved_search: SavedSearch
    email_verified: bool
    whatsapp_verified: bool


def _normalize_phone(phone: str) -> str:
    cleaned = phone.strip().replace(" ", "").replace("-", "")
    if cleaned and not cleaned.startswith("+"):
        cleaned = f"+{cleaned}"
    return cleaned


def _search_name(listing_type: str, location: str | None) -> str:
    place = location.strip() if location else "Suisse"
    label = "Logement" if listing_type == "housing" else "Emploi"
    return f"{label} · {place}"[:120]


def subscribe_public_alert(
    db: Session,
    payload: PublicAlertSignup,
    *,
    auto_verify_channels: bool,
) -> PublicSignupResult:
    api_key = generate_api_token()
    plain_email = str(payload.email).lower()
    now = datetime.now(UTC)

    user = User(
        email_lookup=email_lookup(plain_email),
        email=encrypt_pii(plain_email),
        is_active=True,
        locale=payload.locale,
        api_token_hash=hash_api_token(api_key),
    )
    db.add(user)
    db.flush()

    email_verified = False
    whatsapp_verified = False

    email_channel = NotificationChannel(
        user_id=user.id,
        channel_type=ChannelType.EMAIL,
        channel_address=encrypt_pii(plain_email),
        is_verified=auto_verify_channels,
        is_primary=True,
        verified_at=now if auto_verify_channels else None,
        created_at=now,
    )
    db.add(email_channel)
    email_verified = auto_verify_channels

    if payload.phone:
        phone = _normalize_phone(payload.phone)
        whatsapp_channel = NotificationChannel(
            user_id=user.id,
            channel_type=ChannelType.WHATSAPP,
            channel_address=encrypt_pii(phone),
            is_verified=auto_verify_channels,
            is_primary=False,
            verified_at=now if auto_verify_channels else None,
            created_at=now,
        )
        db.add(whatsapp_channel)
        whatsapp_verified = auto_verify_channels

    saved_search = SavedSearch(
        user_id=user.id,
        name=_search_name(payload.query.listing_type.value, payload.query.location),
        query=payload.query.model_dump(mode="json", exclude_none=True),
        is_active=True,
        created_at=now,
        updated_at=now,
    )
    db.add(saved_search)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise exc

    db.refresh(user)
    db.refresh(saved_search)
    return PublicSignupResult(
        user=user,
        api_key=api_key,
        saved_search=saved_search,
        email_verified=email_verified,
        whatsapp_verified=whatsapp_verified,
    )
