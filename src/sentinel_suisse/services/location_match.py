"""Location search matching — Geneva aliases and nearby communes.

Search is a plain ILIKE substring. Flatfox stores French names (Genève, Les Acacias),
while users type Geneva / Genève / Ginebra. Expand well-known aliases so housing in
the Geneva + border box is findable without a paid geo database.
"""

from __future__ import annotations

_GENEVA_QUERY_ALIASES = frozenset(
    {
        "geneva",
        "geneve",
        "genf",
        "ginebra",
        "ginevra",
    }
)

# Substring terms OR'd when the user searches a Geneva alias. Keep this list to
# communes/postcodes in the product area (canton + nearby France border).
_GENEVA_AREA_TERMS: tuple[str, ...] = (
    "Geneva",
    "Genève",
    "Geneve",
    "Genf",
    "Acacias",
    "Châtelaine",
    "Chatelaine",
    "Lancy",
    "Carouge",
    "Meyrin",
    "Vernier",
    "Onex",
    "Thônex",
    "Thonex",
    "Bernex",
    "Versoix",
    "Aïre",
    "Aire",
    "Chêne-Bougeries",
    "Chêne-Bourg",
    "Plan-les-Ouates",
    "Satigny",
    "Cologny",
    "Veyrier",
    "Grand-Saconnex",
    "Petit-Saconnex",
    "Annemasse",
    "Gaillard",
    "Ferney",
    "Saint-Julien",
    "1201",
    "1202",
    "1203",
    "1204",
    "1205",
    "1206",
    "1207",
    "1208",
    "1209",
    "1212",
    "1213",
    "1214",
    "1216",
    "1217",
    "1218",
    "1219",
    "1220",
    "1224",
    "1225",
    "1226",
    "1227",
    "1228",
    "1231",
    "1232",
    "1233",
    "1234",
    "74100",
    "01210",
    "74160",
    "74240",
)


def _fold(value: str) -> str:
    lowered = value.strip().casefold()
    return (
        lowered.replace("é", "e")
        .replace("è", "e")
        .replace("ê", "e")
        .replace("ë", "e")
        .replace("à", "a")
        .replace("â", "a")
        .replace("ä", "a")
        .replace("ö", "o")
        .replace("ü", "u")
        .replace("ô", "o")
        .replace("î", "i")
        .replace("ï", "i")
        .replace("ç", "c")
        .replace("ñ", "n")
    )


def expand_location_query(query: str) -> list[str]:
    """Return ILIKE needles for a user location string."""
    stripped = query.strip()
    if not stripped:
        return []
    if _fold(stripped) in _GENEVA_QUERY_ALIASES:
        return list(_GENEVA_AREA_TERMS)
    return [stripped]


def location_matches(listing_location: str | None, query: str) -> bool:
    if listing_location is None:
        return False
    hay = listing_location.casefold()
    for term in expand_location_query(query):
        if term.casefold() in hay:
            return True
    return False
