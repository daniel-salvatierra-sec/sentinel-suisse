"""Translate listing title/body into the app language for in-app reading.

Adzuna and similar boards pin one UI language and block website-translate
proxies (translate.goog returns 403). We translate the text we already store
so ES/PT users can read the offer in LinkSwiss before they apply on the
original site (where the browser translator can still help).
"""

from __future__ import annotations

import logging

import httpx

logger = logging.getLogger(__name__)

_SUPPORTED = frozenset({"fr", "de", "es", "pt", "en"})
_MAX_CHUNK = 4500
_TRANSLATE_URL = "https://translate.googleapis.com/translate_a/single"


def _join_segments(data: object) -> str:
    if not isinstance(data, list) or not data:
        return ""
    chunks = data[0]
    if not isinstance(chunks, list):
        return ""
    parts: list[str] = []
    for item in chunks:
        if isinstance(item, list) and item and isinstance(item[0], str):
            parts.append(item[0])
    return "".join(parts)


def _translate_chunk(text: str, lang: str) -> str | None:
    try:
        response = httpx.get(
            _TRANSLATE_URL,
            params={"client": "gtx", "sl": "auto", "tl": lang, "dt": "t", "q": text},
            headers={"User-Agent": "Mozilla/5.0 (compatible; LinkSwiss/1.0)"},
            timeout=8.0,
        )
        response.raise_for_status()
        translated = _join_segments(response.json()).strip()
        return translated or None
    except (httpx.HTTPError, ValueError, TypeError) as exc:
        logger.warning("Listing translate failed: %s", exc)
        return None


def translate_public_text(text: str, lang: str) -> str:
    stripped = text.strip()
    if not stripped or lang not in _SUPPORTED:
        return text
    if len(stripped) <= _MAX_CHUNK:
        return _translate_chunk(stripped, lang) or text
    pieces: list[str] = []
    for start in range(0, len(stripped), _MAX_CHUNK):
        chunk = stripped[start : start + _MAX_CHUNK]
        pieces.append(_translate_chunk(chunk, lang) or chunk)
    return "".join(pieces)


def translate_listing_fields(title: str, body: str, lang: str) -> tuple[str, str]:
    return (
        translate_public_text(title, lang) if title.strip() else title,
        translate_public_text(body, lang) if body.strip() else body,
    )
