"""Known places Sentinela may search — never invent a city outside this catalog."""

from __future__ import annotations

import re
import unicodedata

from sentinel_suisse.services.city_stock import PICKER_CITIES

# Canonical English picker name → zone.
_SWISS: dict[str, str] = {name: "CH" for name in PICKER_CITIES}

_NEIGHBOR: dict[str, str] = {
    "Paris": "FR",
    "Marseille": "FR",
    "Lyon": "FR",
    "Toulouse": "FR",
    "Berlin": "DE",
    "Hamburg": "DE",
    "Munich": "DE",
    "Cologne": "DE",
    "Frankfurt": "DE",
    "Stuttgart": "DE",
    "Dusseldorf": "DE",
    "Leipzig": "DE",
    "Dortmund": "DE",
    "Essen": "DE",
    "Bremen": "DE",
    "Dresden": "DE",
    "Hanover": "DE",
    "Nuremberg": "DE",
    "Duisburg": "DE",
    "Rome": "IT",
    "Milan": "IT",
    "Naples": "IT",
    "Turin": "IT",
    "Palermo": "IT",
    "Genoa": "IT",
}

# France/Switzerland belt: legal jobs; housing uses the border belt, not fake flats.
_BORDER: dict[str, str] = {
    "Annemasse": "FR",
    "Thonon": "FR",
    "Ferney": "FR",
    "Gaillard": "FR",
    "Saint-Julien": "FR",
    "Archamps": "FR",
    "Carouge": "CH",
    "Meyrin": "CH",
    "Vernier": "CH",
    "Lancy": "CH",
    "Onex": "CH",
    "Nyon": "CH",
}

_ALIASES: dict[str, str] = {
    "geneve": "Geneva",
    "genf": "Geneva",
    "ginebra": "Geneva",
    "ginevra": "Geneva",
    "zurich": "Zurich",
    "zurigo": "Zurich",
    "berne": "Bern",
    "berna": "Bern",
    "bale": "Basel",
    "basilea": "Basel",
    "losanna": "Lausanne",
    "luzern": "Lucerne",
    "lucerna": "Lucerne",
    "st gallen": "St. Gallen",
    "sankt gallen": "St. Gallen",
    "saint-gall": "St. Gallen",
    "san galo": "St. Gallen",
    "freiburg": "Fribourg",
    "friburgo": "Fribourg",
    "neuenburg": "Neuchatel",
    "bienne": "Biel",
    "zoug": "Zug",
    "sitten": "Sion",
    "coire": "Chur",
    "parigi": "Paris",
    "marsella": "Marseille",
    "lione": "Lyon",
    "tolosa": "Toulouse",
    "munchen": "Munich",
    "monaco": "Munich",
    "koln": "Cologne",
    "colonia": "Cologne",
    "hannover": "Hanover",
    "nurnberg": "Nuremberg",
    "roma": "Rome",
    "milano": "Milan",
    "napoli": "Naples",
    "napoles": "Naples",
    "torino": "Turin",
    "genova": "Genoa",
    "thonon-les-bains": "Thonon",
    "ferney-voltaire": "Ferney",
    "st julien": "Saint-Julien",
    "saint julien en genevois": "Saint-Julien",
    "annemasse": "Annemasse",
}


def fold(value: str) -> str:
    decomposed = unicodedata.normalize("NFD", value.strip().lower())
    return "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")


def _canonical_zone() -> dict[str, str]:
    merged = dict(_SWISS)
    merged.update(_NEIGHBOR)
    merged.update(_BORDER)
    return merged


def resolve_place(token: str) -> tuple[str, str] | None:
    """Return (canonical_city, zone) or None if unknown."""
    folded = fold(token).replace("-", " ").replace(".", " ")
    folded = " ".join(folded.split())
    catalog = _canonical_zone()
    for name, zone in catalog.items():
        if fold(name) == folded:
            return name, zone
    aliased = _ALIASES.get(folded)
    if aliased and aliased in catalog:
        return aliased, catalog[aliased]
    return None


def find_place_in_text(text: str) -> tuple[str, str] | None:
    """Longest known place mentioned in free text (whole tokens only)."""
    folded = fold(text)
    catalog = _canonical_zone()
    names = list(catalog.keys()) + list(_ALIASES.keys())
    names.sort(key=len, reverse=True)
    best: tuple[str, str] | None = None
    best_len = 0
    for name in names:
        needle = fold(name)
        if len(needle) < 3:
            continue
        if not re.search(rf"(?<![a-z0-9]){re.escape(needle)}(?![a-z0-9])", folded):
            continue
        resolved = resolve_place(name)
        if resolved and len(needle) > best_len:
            best = resolved
            best_len = len(needle)
    return best
