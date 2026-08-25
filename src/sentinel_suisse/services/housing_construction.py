"""Detect off-plan / under-construction housing from flags and listing text."""

from __future__ import annotations

import unicodedata
from typing import Any

from sqlalchemy import or_
from sqlalchemy.sql.elements import ColumnElement

from sentinel_suisse.models.enums import ListingType
from sentinel_suisse.models.listing import Listing

# Explicit phrases only — "Neubau" alone is often a finished new build.
CONSTRUCTION_NEEDLES: tuple[str, ...] = (
    "en construction",
    "en construcción",
    "en construccion",
    "en cours de construction",
    "sur plan",
    "vente sur plan",
    "im bau",
    "in bau",
    "under construction",
    "off-plan",
    "off plan",
    "en obra",
    "em construção",
    "em construcao",
    "programme neuf",
    "rohbau",
    "livraison prévue",
    "livraison prevue",
    "à construire",
    "a construire",
)


def _fold(value: str) -> str:
    normalized = unicodedata.normalize("NFD", value.casefold())
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")


def text_looks_under_construction(title: str | None, description: str | None) -> bool:
    hay = _fold(f"{title or ''} {description or ''}")
    if not hay.strip():
        return False
    return any(_fold(needle) in hay for needle in CONSTRUCTION_NEEDLES)


def payload_says_construction(payload: dict[str, Any] | None) -> bool:
    if not isinstance(payload, dict):
        return False
    for key in ("is_under_construction", "off_plan", "is_off_plan"):
        if payload.get(key) is True:
            return True
    attrs = payload.get("attributes")
    names: list[str] = []
    if isinstance(attrs, list):
        for item in attrs:
            if isinstance(item, dict) and item.get("name"):
                names.append(_fold(str(item["name"])))
    blob = " ".join(names)
    return any(_fold(needle) in blob for needle in CONSTRUCTION_NEEDLES)


def resolve_under_construction(
    *,
    listing_type: ListingType | str,
    title: str | None,
    description: str | None,
    flagged: bool | None,
    payload: dict[str, Any] | None = None,
) -> bool | None:
    if flagged is True:
        return True
    kind = listing_type.value if isinstance(listing_type, ListingType) else listing_type
    if kind != ListingType.HOUSING.value:
        return flagged
    if payload_says_construction(payload) or text_looks_under_construction(title, description):
        return True
    return flagged


def listing_looks_under_construction(listing: Listing) -> bool:
    resolved = resolve_under_construction(
        listing_type=listing.listing_type,
        title=listing.title,
        description=listing.description,
        flagged=listing.is_under_construction,
        payload=listing.raw_payload,
    )
    return resolved is True


def construction_match_clause() -> ColumnElement[bool]:
    clauses: list[ColumnElement[bool]] = [Listing.is_under_construction.is_(True)]
    for needle in CONSTRUCTION_NEEDLES:
        like = f"%{needle}%"
        clauses.append(Listing.title.ilike(like))
        clauses.append(Listing.description.ilike(like))
    return or_(*clauses)
