"""Location search matching — Geneva aliases and nearby communes.

Search is a plain ILIKE substring. Flatfox stores French names (Genève, Les Acacias),
while users type Geneva / Genève / Ginebra. Expand well-known aliases so housing in
the Geneva + border box is findable without a paid geo database.
"""

from __future__ import annotations

import re

_GENEVA_QUERY_ALIASES = frozenset(
    {
        "geneva",
        "geneve",
        "genf",
        "ginebra",
        "ginevra",
        "gva",
        "cointrin",
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
    "GVA",
    "Cointrin",
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


def _alias_set(*names: str) -> frozenset[str]:
    return frozenset(_fold(name) for name in names)


_ZURICH_TERMS: tuple[str, ...] = (
    "Zurich",
    "Zürich",
    "Zurigo",
    "Kloten",
    "ZRH",
)
_BERN_TERMS: tuple[str, ...] = (
    "Bern",
    "Berne",
    "Berna",
    "BRN",
)
_BASEL_TERMS: tuple[str, ...] = (
    "Basel",
    "Bâle",
    "Bale",
    "Basilea",
    "BSL",
    "EuroAirport",
)
_LAUSANNE_TERMS: tuple[str, ...] = (
    "Lausanne",
    "Losanna",
    "Renens",
    "Ecublens",
    "Pully",
    "Prilly",
    "Bussigny",
    "Crissier",
    "Epalinges",
    "Jouxtens",
    "Le Mont",
    "Chavannes",
    "Mobi-Lausanne",
    "Transports publics",
    "1000",
    "1003",
    "1004",
    "1005",
    "1006",
    "1007",
    "1010",
    "1012",
    "1018",
    "1020",
    "1022",
    "1023",
    "1024",
    "1025",
    "1026",
    "1027",
    "1028",
    "1030",
)
_LUGANO_TERMS: tuple[str, ...] = ("Lugano",)
_LUCERNE_TERMS: tuple[str, ...] = ("Lucerne", "Luzern", "Lucerna")
_ST_GALLEN_TERMS: tuple[str, ...] = (
    "St. Gallen",
    "Sankt Gallen",
    "Saint-Gall",
    "San Galo",
)
_WINTERTHUR_TERMS: tuple[str, ...] = ("Winterthur",)
_FRIBOURG_TERMS: tuple[str, ...] = ("Fribourg", "Freiburg", "Friburgo")
_NEUCHATEL_TERMS: tuple[str, ...] = ("Neuchatel", "Neuchâtel", "Neuenburg")
_BIEL_TERMS: tuple[str, ...] = ("Biel", "Bienne", "Biel/Bienne")
_ZUG_TERMS: tuple[str, ...] = ("Zug", "Zoug", "Zugo")
_SION_TERMS: tuple[str, ...] = ("Sion", "Sitten")
_CHUR_TERMS: tuple[str, ...] = ("Chur", "Coire", "Coira")
_BELLINZONA_TERMS: tuple[str, ...] = ("Bellinzona",)
_SCHAFFHAUSEN_TERMS: tuple[str, ...] = ("Schaffhausen", "Schaffhouse")
_THUN_TERMS: tuple[str, ...] = ("Thun", "Thoune")
_AARAU_TERMS: tuple[str, ...] = ("Aarau",)
_CHAUX_TERMS: tuple[str, ...] = ("La Chaux-de-Fonds", "Chaux-de-Fonds")

_CITY_GROUPS: tuple[tuple[frozenset[str], tuple[str, ...]], ...] = (
    (_GENEVA_QUERY_ALIASES, _GENEVA_AREA_TERMS),
    (
        _alias_set("zurich", "zürich", "zurigo", "zrh", "kloten", "zurich airport"),
        _ZURICH_TERMS,
    ),
    (_alias_set("bern", "berne", "berna", "brn"), _BERN_TERMS),
    (
        _alias_set("basel", "bâle", "bale", "basilea", "bsl", "euroairport"),
        _BASEL_TERMS,
    ),
    (_alias_set("lausanne", "losanna", "tl", "mobi-lausanne"), _LAUSANNE_TERMS),
    (_alias_set("lugano"), _LUGANO_TERMS),
    (_alias_set("lucerne", "luzern", "lucerna"), _LUCERNE_TERMS),
    (
        _alias_set("st. gallen", "st gallen", "sankt gallen", "saint-gall", "san galo"),
        _ST_GALLEN_TERMS,
    ),
    (_alias_set("winterthur"), _WINTERTHUR_TERMS),
    (_alias_set("fribourg", "freiburg", "friburgo"), _FRIBOURG_TERMS),
    (_alias_set("neuchatel", "neuchâtel", "neuenburg"), _NEUCHATEL_TERMS),
    (_alias_set("biel", "bienne", "biel/bienne"), _BIEL_TERMS),
    (_alias_set("zug", "zoug", "zugo"), _ZUG_TERMS),
    (_alias_set("sion", "sitten"), _SION_TERMS),
    (_alias_set("chur", "coire", "coira"), _CHUR_TERMS),
    (_alias_set("bellinzona"), _BELLINZONA_TERMS),
    (_alias_set("schaffhausen", "schaffhouse"), _SCHAFFHAUSEN_TERMS),
    (_alias_set("thun", "thoune"), _THUN_TERMS),
    (_alias_set("aarau"), _AARAU_TERMS),
    (_alias_set("la chaux-de-fonds", "chaux-de-fonds"), _CHAUX_TERMS),
    (_alias_set("nyon"), ("Nyon",)),
    (_alias_set("morges"), ("Morges",)),
    (_alias_set("vevey"), ("Vevey",)),
    (_alias_set("montreux"), ("Montreux",)),
    (_alias_set("yverdon", "yverdon-les-bains"), ("Yverdon", "Yverdon-les-Bains")),
    (_alias_set("bulle"), ("Bulle",)),
    (_alias_set("martigny"), ("Martigny",)),
    (_alias_set("sierre", "siders"), ("Sierre", "Siders")),
    (_alias_set("monthey"), ("Monthey",)),
    (_alias_set("delemont", "delémont", "delsberg"), ("Delemont", "Delémont", "Delsberg")),
    (_alias_set("olten"), ("Olten",)),
    (_alias_set("baden"), ("Baden",)),
    (_alias_set("wil"), ("Wil",)),
    (_alias_set("uster"), ("Uster",)),
    (_alias_set("frauenfeld"), ("Frauenfeld",)),
    (_alias_set("solothurn", "soleure", "soletta"), ("Solothurn", "Soleure", "Soletta")),
    (_alias_set("langenthal"), ("Langenthal",)),
    (_alias_set("interlaken"), ("Interlaken",)),
    (_alias_set("liestal"), ("Liestal",)),
    (_alias_set("kreuzlingen"), ("Kreuzlingen",)),
    (_alias_set("locarno"), ("Locarno",)),
    (_alias_set("mendrisio"), ("Mendrisio",)),
    (_alias_set("chiasso"), ("Chiasso",)),
    (_alias_set("brig", "brigue", "briga"), ("Brig", "Brigue", "Briga")),
    (_alias_set("schwyz"), ("Schwyz",)),
    (_alias_set("emmen"), ("Emmen",)),
    (_alias_set("dietikon"), ("Dietikon",)),
    (_alias_set("horgen"), ("Horgen",)),
)


def expand_location_query(query: str) -> list[str]:
    """Return ILIKE needles for a user location string."""
    stripped = query.strip()
    if not stripped:
        return []
    folded = _fold(stripped)
    for aliases, terms in _CITY_GROUPS:
        if folded in aliases:
            return list(terms)
    return [stripped]


def location_matches(listing_location: str | None, query: str) -> bool:
    if listing_location is None:
        return False
    hay = listing_location
    for term in expand_location_query(query):
        if _term_in_location(hay, term):
            return True
    return False


def _term_in_location(haystack: str, term: str) -> bool:
    """Whole-token match so 'Sion' does not hit 'pension' / 'décision'."""
    stripped = term.strip()
    if not stripped:
        return False
    pattern = rf"(?<![\w]){re.escape(stripped)}(?![\w])"
    return re.search(pattern, haystack, flags=re.IGNORECASE) is not None
