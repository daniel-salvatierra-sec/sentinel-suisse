"""Expand job-word searches so Spanish/French queries match CH titles."""

from __future__ import annotations

import unicodedata


def _fold(value: str) -> str:
    normalized = unicodedata.normalize("NFD", value.strip().casefold())
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")


# aliases (folded) → ILIKE needles as they appear in Swiss job ads
_JOB_TERM_GROUPS: tuple[tuple[frozenset[str], tuple[str, ...]], ...] = (
    (
        frozenset(
            {
                "fleuriste",
                "fleuristes",
                "florist",
                "florists",
                "floristin",
                "florista",
                "fiorista",
                "floristeria",
                "floristerie",
                "blumenfach",
                "blumenfachverkaufer",
                "blumenfachverkaeufer",
            }
        ),
        ("florist", "fleuriste", "floristin", "fiorista", "florista", "Blumenfach"),
    ),
    (
        frozenset(
            {
                "cajero",
                "cajera",
                "cajeros",
                "cashier",
                "caissier",
                "caissiere",
                "kassierer",
                "kassierin",
                "caixa",
            }
        ),
        ("caissier", "cashier", "Kassierer", "Kassierin", "cajero"),
    ),
)


def expand_text_query(query: str) -> list[str]:
    """Needles for title/description ILIKE. Unknown words stay as typed."""
    stripped = query.strip()
    if not stripped:
        return []
    folded = _fold(stripped)
    for aliases, needles in _JOB_TERM_GROUPS:
        if folded in aliases:
            return list(needles)
    return [stripped]


def query_looks_like_job(query: str) -> bool:
    folded = _fold(query)
    if not folded:
        return False
    for aliases, _needles in _JOB_TERM_GROUPS:
        if folded in aliases:
            return True
        if any(token in aliases for token in folded.split()):
            return True
    return False
