"""Alert notification copy in five mandatory languages."""

from sentinel_suisse.i18n import resolve_locale
from sentinel_suisse.models.listing import Listing
from sentinel_suisse.notifications.base import AlertMessage

_ALERT_COPY: dict[str, dict[str, str]] = {
    "fr": {
        "email_intro": "Nouvelle correspondance pour la recherche : {search_name}",
        "location": "Lieu",
        "price": "Prix",
        "link": "Lien",
        "price_na": "non communiqué",
        "subject_prefix": "Sentinel Suisse",
        "whatsapp_price_suffix": "CHF",
    },
    "de": {
        "email_intro": "Neuer Treffer für die Suche: {search_name}",
        "location": "Ort",
        "price": "Preis",
        "link": "Link",
        "price_na": "k. A.",
        "subject_prefix": "Sentinel Suisse",
        "whatsapp_price_suffix": "CHF",
    },
    "es": {
        "email_intro": "Nueva coincidencia para la búsqueda: {search_name}",
        "location": "Ubicación",
        "price": "Precio",
        "link": "Enlace",
        "price_na": "no indicado",
        "subject_prefix": "Sentinel Suisse",
        "whatsapp_price_suffix": "CHF",
    },
    "pt": {
        "email_intro": "Nova correspondência para a pesquisa: {search_name}",
        "location": "Localização",
        "price": "Preço",
        "link": "Ligação",
        "price_na": "não indicado",
        "subject_prefix": "Sentinel Suisse",
        "whatsapp_price_suffix": "CHF",
    },
    "en": {
        "email_intro": "New match for saved search: {search_name}",
        "location": "Location",
        "price": "Price",
        "link": "Link",
        "price_na": "n/a",
        "subject_prefix": "Sentinel Suisse",
        "whatsapp_price_suffix": "CHF",
    },
}


def _copy(locale: str) -> dict[str, str]:
    return _ALERT_COPY[resolve_locale(locale)]


def _format_price(listing: Listing, locale: str) -> str:
    if listing.price is None:
        return _copy(locale)["price_na"]
    return str(listing.price)


def format_email_alert(message: AlertMessage) -> tuple[str, str]:
    """Return (subject, plain-text body) for SMTP."""
    locale = resolve_locale(message.locale)
    strings = _copy(locale)
    listing = message.listing
    body = (
        f"{strings['email_intro'].format(search_name=message.saved_search.name)}\n\n"
        f"{listing.title}\n"
        f"{strings['location']}: {listing.location}\n"
        f"{strings['price']}: {_format_price(listing, locale)}\n"
        f"{strings['link']}: {listing.source_url}\n"
    )
    subject = f"{strings['subject_prefix']}: {listing.title}"[:120]
    return subject, body


def format_whatsapp_alert(message: AlertMessage) -> str:
    """Return WhatsApp text body (Markdown-style bold for search name)."""
    locale = resolve_locale(message.locale)
    strings = _copy(locale)
    listing = message.listing
    price = _format_price(listing, locale)
    if listing.price is not None:
        price = f"{price} {strings['whatsapp_price_suffix']}"
    return (
        f"*{message.saved_search.name}*\n"
        f"{listing.title}\n"
        f"{listing.location} — {price}\n"
        f"{listing.source_url}"
    )


def format_console_summary(message: AlertMessage) -> str:
    locale = resolve_locale(message.locale)
    strings = _copy(locale)
    listing = message.listing
    return (
        f"[{locale}] {strings['email_intro'].format(search_name=message.saved_search.name)} | "
        f"{listing.title} | {listing.source_url}"
    )
