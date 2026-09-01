"""Regex / keyword intent parser — works with the LLM off."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Literal

from sentinel_suisse.services.sentinela_cities import find_place_in_text, fold

Mode = Literal["housing", "job"]
Intent = Literal[
    "search",
    "map",
    "alert",
    "open_first",
    "cheaper",
    "how_apply",
    "need_city",
    "unknown_city",
    "out_of_scope",
]
Zone = Literal["CH", "FR", "DE", "IT"]

_HOUSING = (
    "logement",
    "appartement",
    "appart",
    "piso",
    "vivienda",
    "wohnung",
    "miete",
    "apartamento",
    "moradia",
    "casa",
    "studio",
    "habitacion",
    "zimmer",
    "pieces",
    "piezas",
    "tipologia",
)
_JOB = (
    "emploi",
    "empleo",
    "job",
    "trabajo",
    "emprego",
    "stelle",
    "stellen",
    "lavoro",
    "arbeit",
    "work",
    "vacante",
    "offre",
)
_MAP = ("mapa", "carte", "karte", "map", "cartina")
_ALERT = (
    "avisame",
    "avisa",
    "alerta",
    "alerte",
    "alarm",
    "notify",
    "aviso",
    "prevenir",
    "avisar",
    "notifica",
)
_FIRST = ("primero", "premier", "erste", "first", "primeiro", "erster", "primera")
_CHEAP = ("barato", "moins cher", "gunstiger", "cheaper", "mais barato", "pas cher", "guter preis")
_APPLY = (
    "como aplico",
    "comment postuler",
    "bewerb",
    "how to apply",
    "candidat",
    "postuler",
    "como me candidato",
)
_ZONE_FR = ("france", "francia", "frankreich", "francesa")
_ZONE_DE = ("allemagne", "alemania", "deutschland", "alemana")
_ZONE_IT = ("italie", "italia", "italien", "italiana")
_ZONE_CH = ("suisse", "suiza", "schweiz", "switzerland", "svizzera")

_STOP = frozenset(
    {
        "un",
        "una",
        "el",
        "la",
        "le",
        "les",
        "the",
        "a",
        "en",
        "in",
        "de",
        "du",
        "des",
        "cerca",
        "pres",
        "near",
        "bei",
        "per",
        "por",
        "para",
        "pour",
        "busco",
        "cherche",
        "suche",
        "looking",
        "procuro",
        "quiero",
        "veux",
        "want",
        "etwas",
        "algo",
        "quelque",
        "something",
    }
)

_PLACE_HINT = re.compile(
    r"\b(?:en|à|a|in|near|cerca de|près d[e']|bei|em)\s+([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ\-']{2,})",
    re.IGNORECASE,
)

_ROOMS = re.compile(r"\b(\d(?:[.,]\d)?)\s*(?:p(?:i[eè]ces?|iezas?|ezos?)|zimmer|rooms?)?\b", re.I)
_PRICE = re.compile(
    r"(?:chf|frs?|sfr|jusqu['’]?a|hasta|ate|bis|max(?:imum)?|until|sous|bajo)?\s*"
    r"(\d{1,2}(?:[.'\s]\d{3})|\d{3,5})\b",
    re.I,
)
_PARKING = ("parking", "garage", "estacionamiento")
_NEW = ("neuf", "nuevo", "neubau", "construction", "obras", "new-build", "novo")


@dataclass
class SentinelaIntent:
    mode: Mode | None = None
    zone: Zone | None = None
    city: str | None = None
    rooms: str | None = None
    price_max: int | None = None
    has_parking: bool | None = None
    under_construction: bool | None = None
    sort: str | None = None
    intent: Intent = "out_of_scope"
    unknown_city: str | None = None
    chips: list[str] = field(default_factory=list)


def _has_any(folded: str, words: tuple[str, ...]) -> bool:
    return any(word in folded for word in words)


def _parse_rooms(text: str) -> str | None:
    studio = fold(text)
    if "studio" in studio or "etude" in studio and "studio" in studio:
        if re.search(r"\bstudio\b", studio):
            return "studio"
    found: list[str] = []
    for match in _ROOMS.finditer(text):
        raw = match.group(1).replace(",", ".")
        try:
            value = float(raw)
        except ValueError:
            continue
        if value in {1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0} or (
            value == 1 and "studio" not in studio
        ):
            key = str(value).replace(".0", "")
            if value in {1.5, 2.5, 3.5, 4.5, 5.5}:
                key = f"{value:.1f}"
            elif value >= 5:
                key = "5"
            elif value >= 4:
                key = "4"
            found.append(key)
    return found[0] if found else None


def _parse_price(text: str, rooms: str | None) -> int | None:
    prices: list[int] = []
    for match in _PRICE.finditer(text):
        digits = re.sub(r"[^\d]", "", match.group(1))
        if not digits:
            continue
        value = int(digits)
        if rooms and rooms != "studio":
            try:
                room_n = float(rooms)
            except ValueError:
                room_n = 0
            if abs(value - room_n) < 0.01:
                continue
        if 400 <= value <= 20000:
            prices.append(value)
    return prices[-1] if prices else None


def _hint_unknown_city(text: str) -> str | None:
    match = _PLACE_HINT.search(text)
    if not match:
        return None
    token = match.group(1)
    if fold(token) in _STOP:
        return None
    if find_place_in_text(token):
        return None
    if find_place_in_text(text):
        return None
    return token


def parse_turn(
    message: str,
    *,
    ui_mode: Mode | None = None,
    ui_zone: Zone | None = None,
    has_open_listing: bool = False,
) -> SentinelaIntent:
    text = message.strip()
    folded = fold(text)
    intent = SentinelaIntent(mode=ui_mode, zone=ui_zone)

    place = find_place_in_text(text)
    if place:
        intent.city, zone = place
        intent.zone = zone  # type: ignore[assignment]

    unknown = _hint_unknown_city(text)
    if unknown and not place:
        intent.unknown_city = unknown
        intent.intent = "unknown_city"
        intent.chips = []
        return intent

    if _has_any(folded, _HOUSING) and not _has_any(folded, _JOB):
        intent.mode = "housing"
    elif _has_any(folded, _JOB) and not _has_any(folded, _HOUSING):
        intent.mode = "job"

    if _has_any(folded, _ZONE_FR):
        intent.zone = "FR"
    elif _has_any(folded, _ZONE_DE):
        intent.zone = "DE"
    elif _has_any(folded, _ZONE_IT):
        intent.zone = "IT"
    elif _has_any(folded, _ZONE_CH):
        intent.zone = "CH"

    intent.rooms = _parse_rooms(text)
    intent.price_max = _parse_price(text, intent.rooms)
    if _has_any(folded, _PARKING):
        intent.has_parking = True
    if _has_any(folded, _NEW):
        intent.under_construction = True

    if _has_any(folded, _MAP):
        intent.intent = "map"
        intent.chips = ["keep_looking"]
        return intent
    if _has_any(folded, _ALERT):
        intent.intent = "alert"
        intent.chips = []
        return intent
    if _has_any(folded, _FIRST):
        intent.intent = "open_first"
        intent.chips = ["on_map", "create_alert"]
        return intent
    if _has_any(folded, _CHEAP):
        intent.intent = "cheaper"
        intent.sort = "price_asc"
        if intent.mode is None:
            intent.mode = ui_mode or "housing"
        intent.chips = ["see_first", "create_alert"]
        return intent
    if _has_any(folded, _APPLY) or (has_open_listing and "aplic" in folded):
        intent.intent = "how_apply"
        intent.chips = ["keep_looking"]
        return intent

    searchish = any(
        [
            intent.city,
            intent.rooms,
            intent.price_max,
            intent.has_parking,
            intent.under_construction,
            _has_any(folded, _HOUSING),
            _has_any(folded, _JOB),
        ]
    )
    if searchish:
        if intent.mode is None:
            if intent.rooms or intent.price_max:
                intent.mode = "housing"
            else:
                intent.mode = ui_mode
        if intent.mode == "housing" and not intent.city:
            intent.intent = "need_city"
            intent.chips = []
            return intent
        intent.intent = "search"
        intent.chips = ["see_first", "create_alert", "on_map"]
        return intent

    intent.intent = "out_of_scope"
    intent.chips = ["look_home", "look_job"]
    return intent
