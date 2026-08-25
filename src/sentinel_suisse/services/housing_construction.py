"""Detect new-build / first-letting housing ready for applications.

Product intent: projets neufs à la location / Erstvermietung — finished (or
just-delivered) buildings where candidates can apply now. Not sur plan / still
under construction.
"""

from __future__ import annotations

import unicodedata
from typing import Any

from sqlalchemy import and_, not_, or_
from sqlalchemy.sql.elements import ColumnElement

from sentinel_suisse.models.enums import ListingType
from sentinel_suisse.models.listing import Listing

# Ready-to-apply new projects (Comptoir-style "projets neufs à la location").
NEW_PROJECT_NEEDLES: tuple[str, ...] = (
    "erstvermietung",
    "erste vermietung",
    "neuvermietung",
    "première location",
    "premiere location",
    "projet neuf",
    "projets neufs",
    "programme neuf",
    "promotion immobilière",
    "promotion immobiliere",
    "immeubles neufs",
    "immeuble neuf",
    "bâtiment neuf",
    "batiment neuf",
    "logements neufs",
    "logement neuf",
    "neubau",
    "neubauwohnung",
    "neu erbaut",
    "neu erstellt",
    "first occupancy",
    "first letting",
    "new development",
    "proyecto nuevo",
    "proyectos nuevos",
    "obra nueva",
    "primeira locação",
    "primeira locacao",
    "projeto novo",
    "projetos novos",
)

# Still building / off-plan — exclude even if a new-project needle also appears.
OFF_PLAN_NEEDLES: tuple[str, ...] = (
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
    "rohbau",
    "livraison prévue",
    "livraison prevue",
    "à construire",
    "a construire",
)


def _fold(value: str) -> str:
    normalized = unicodedata.normalize("NFD", value.casefold())
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")


def _haystack(title: str | None, description: str | None) -> str:
    return _fold(f"{title or ''} {description or ''}")


def text_looks_off_plan(title: str | None, description: str | None) -> bool:
    hay = _haystack(title, description)
    if not hay.strip():
        return False
    return any(_fold(needle) in hay for needle in OFF_PLAN_NEEDLES)


def text_looks_under_construction(title: str | None, description: str | None) -> bool:
    """True for ready-to-apply new projects (legacy name kept for call sites)."""
    hay = _haystack(title, description)
    if not hay.strip():
        return False
    if any(_fold(needle) in hay for needle in OFF_PLAN_NEEDLES):
        return False
    return any(_fold(needle) in hay for needle in NEW_PROJECT_NEEDLES)


def payload_says_construction(payload: dict[str, Any] | None) -> bool:
    if not isinstance(payload, dict):
        return False
    if payload.get("off_plan") is True or payload.get("is_off_plan") is True:
        return False
    if payload.get("is_new_building") is True:
        return True
    if payload.get("is_under_construction") is True:
        # Connector flag: treat as new-project signal unless text says off-plan.
        return True
    attrs = payload.get("attributes")
    names: list[str] = []
    if isinstance(attrs, list):
        for item in attrs:
            if isinstance(item, dict) and item.get("name"):
                names.append(_fold(str(item["name"])))
    blob = " ".join(names)
    if any(_fold(needle) in blob for needle in OFF_PLAN_NEEDLES):
        return False
    return any(_fold(needle) in blob for needle in NEW_PROJECT_NEEDLES)


def resolve_under_construction(
    *,
    listing_type: ListingType | str,
    title: str | None,
    description: str | None,
    flagged: bool | None,
    payload: dict[str, Any] | None = None,
) -> bool | None:
    kind = listing_type.value if isinstance(listing_type, ListingType) else listing_type
    if kind != ListingType.HOUSING.value:
        return flagged
    if text_looks_off_plan(title, description):
        return False
    if isinstance(payload, dict) and (
        payload.get("off_plan") is True or payload.get("is_off_plan") is True
    ):
        return False
    if text_looks_under_construction(title, description):
        return True
    if payload_says_construction(payload):
        return True
    if flagged is True:
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


def _text_ilike_any(needles: tuple[str, ...]) -> ColumnElement[bool]:
    clauses: list[ColumnElement[bool]] = []
    for needle in needles:
        like = f"%{needle}%"
        clauses.append(Listing.title.ilike(like))
        clauses.append(Listing.description.ilike(like))
    return or_(*clauses)


def construction_match_clause() -> ColumnElement[bool]:
    positive = or_(
        Listing.is_under_construction.is_(True),
        _text_ilike_any(NEW_PROJECT_NEEDLES),
    )
    return and_(positive, not_(_text_ilike_any(OFF_PLAN_NEEDLES)))
