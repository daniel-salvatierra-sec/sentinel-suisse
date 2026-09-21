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
        "open_app": "Ouvrir dans LinkSwiss",
        "open_source": "Offre originale",
        "price_na": "non communiqué",
        "subject_prefix": "LinkSwiss",
        "whatsapp_price_suffix": "CHF",
    },
    "de": {
        "email_intro": "Neuer Treffer für die Suche: {search_name}",
        "location": "Ort",
        "price": "Preis",
        "link": "Link",
        "open_app": "In LinkSwiss öffnen",
        "open_source": "Originalangebot",
        "price_na": "k. A.",
        "subject_prefix": "LinkSwiss",
        "whatsapp_price_suffix": "CHF",
    },
    "es": {
        "email_intro": "Nueva coincidencia para la búsqueda: {search_name}",
        "location": "Ubicación",
        "price": "Precio",
        "link": "Enlace",
        "open_app": "Abrir en LinkSwiss",
        "open_source": "Oferta original",
        "price_na": "no indicado",
        "subject_prefix": "LinkSwiss",
        "whatsapp_price_suffix": "CHF",
    },
    "pt": {
        "email_intro": "Nova correspondência para a pesquisa: {search_name}",
        "location": "Localização",
        "price": "Preço",
        "link": "Ligação",
        "open_app": "Abrir no LinkSwiss",
        "open_source": "Oferta original",
        "price_na": "não indicado",
        "subject_prefix": "LinkSwiss",
        "whatsapp_price_suffix": "CHF",
    },
    "en": {
        "email_intro": "New match for saved search: {search_name}",
        "location": "Location",
        "price": "Price",
        "link": "Link",
        "open_app": "Open in LinkSwiss",
        "open_source": "Original listing",
        "price_na": "n/a",
        "subject_prefix": "LinkSwiss",
        "whatsapp_price_suffix": "CHF",
    },
}


def _copy(locale: str) -> dict[str, str]:
    return _ALERT_COPY[resolve_locale(locale)]


def _format_price(listing: Listing, locale: str) -> str:
    if listing.price is None:
        return _copy(locale)["price_na"]
    return str(listing.price)


def listing_app_url(app_url: str, listing_id: int | None) -> str:
    """Deep link that opens this listing inside LinkSwiss."""
    base = (app_url or "").rstrip("/")
    if not base or listing_id is None:
        return ""
    return f"{base}/?listing={listing_id}"


def _alert_links(listing: Listing, strings: dict[str, str], app_url: str) -> str:
    app_link = listing_app_url(app_url, listing.id)
    source = listing.source_url or ""
    parts: list[str] = []
    if app_link:
        parts.append(f"{strings['open_app']}:\n{app_link}")
    if source and source != app_link:
        label = strings["open_source"] if app_link else strings["link"]
        parts.append(f"{label}:\n{source}")
    return "\n\n".join(parts)


def format_email_alert(message: AlertMessage, *, app_url: str = "") -> tuple[str, str]:
    """Return (subject, plain-text body) for SMTP."""
    locale = resolve_locale(message.locale)
    strings = _copy(locale)
    listing = message.listing
    links = _alert_links(listing, strings, app_url)
    body = (
        f"{strings['email_intro'].format(search_name=message.saved_search.name)}\n\n"
        f"{listing.title}\n"
        f"{strings['location']}: {listing.location}\n"
        f"{strings['price']}: {_format_price(listing, locale)}\n"
    )
    if links:
        body += f"\n{links}\n"
    subject = f"{strings['subject_prefix']}: {listing.title}"[:120]
    return subject, body


def format_whatsapp_alert(message: AlertMessage, *, app_url: str = "") -> str:
    """Return WhatsApp text body (Markdown-style bold for search name)."""
    locale = resolve_locale(message.locale)
    strings = _copy(locale)
    listing = message.listing
    price = _format_price(listing, locale)
    if listing.price is not None:
        price = f"{price} {strings['whatsapp_price_suffix']}"
    app_link = listing_app_url(app_url, listing.id)
    source = listing.source_url or ""
    lines = [
        f"*{message.saved_search.name}*",
        listing.title,
        f"{listing.location} — {price}",
    ]
    # Put the in-app URL first so WhatsApp previews a clickable LinkSwiss card.
    if app_link:
        lines.append(app_link)
    if source and source != app_link:
        lines.append(source)
    return "\n".join(lines)


def format_console_summary(message: AlertMessage, *, app_url: str = "") -> str:
    locale = resolve_locale(message.locale)
    strings = _copy(locale)
    listing = message.listing
    url = listing_app_url(app_url, listing.id) or listing.source_url
    return (
        f"[{locale}] {strings['email_intro'].format(search_name=message.saved_search.name)} | "
        f"{listing.title} | {url}"
    )
