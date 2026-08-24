"""Turn a phone number or https URL into a contact link (WhatsApp or web)."""

from __future__ import annotations

_MIN_DIGITS = 8


class ContactLinkError(ValueError):
    """Raised when the contact field is neither a phone nor https."""


def normalize_contact_link(value: str) -> str:
    """Accept https URLs or phone numbers; phones become https://wa.me/<digits>."""
    raw = value.strip()
    if not raw:
        msg = "contact is required"
        raise ContactLinkError(msg)

    lowered = raw.lower()
    if lowered.startswith("https://"):
        return raw
    if lowered.startswith("http://"):
        msg = "use https"
        raise ContactLinkError(msg)
    if lowered.startswith("wa.me/") or lowered.startswith("www."):
        return f"https://{raw.lstrip('/')}"

    digits = "".join(ch for ch in raw if ch.isdigit())
    if raw.startswith("+"):
        digits = "".join(ch for ch in raw if ch.isdigit())
    elif digits.startswith("00"):
        digits = digits[2:]
    elif digits.startswith("0") and len(digits) >= 9:
        digits = "41" + digits[1:]

    if len(digits) < _MIN_DIGITS:
        msg = "phone or https URL required"
        raise ContactLinkError(msg)
    return f"https://wa.me/{digits}"
