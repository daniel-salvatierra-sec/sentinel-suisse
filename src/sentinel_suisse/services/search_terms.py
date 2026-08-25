"""Expand job-word searches so Spanish/French queries match CH titles."""

from __future__ import annotations

import unicodedata


def _fold(value: str) -> str:
    normalized = unicodedata.normalize("NFD", value.strip().casefold())
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")


def _group(aliases: set[str], needles: tuple[str, ...]) -> tuple[frozenset[str], tuple[str, ...]]:
    return frozenset(_fold(item) for item in aliases), needles


# aliases (folded) → ILIKE needles as they appear in Swiss job ads
_JOB_TERM_GROUPS: tuple[tuple[frozenset[str], tuple[str, ...]], ...] = (
    _group(
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
        },
        ("florist", "fleuriste", "floristin", "fiorista", "florista", "Blumenfach"),
    ),
    _group(
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
        },
        ("caissier", "cashier", "Kassierer", "Kassierin", "cajero"),
    ),
    _group(
        {
            "infirmier",
            "infirmiere",
            "infirmiers",
            "infirmieres",
            "nurse",
            "nursing",
            "enfermero",
            "enfermera",
            "enfermeiro",
            "enfermeira",
            "krankenpfleger",
            "krankenschwester",
            "pflege",
            "soignant",
            "soignante",
        },
        ("infirmier", "infirmière", "nursing", "Pflege", "Krankenpfleger", "soignant"),
    ),
    _group(
        {
            "developpeur",
            "developpeuse",
            "developpeurs",
            "developer",
            "developers",
            "desarrollador",
            "programador",
            "programmeur",
            "software",
            "informatique",
            "informatico",
        },
        (
            "développeur",
            "developpeur",
            "developer",
            "software",
            "programmeur",
            "informatique",
        ),
    ),
    _group(
        {
            "chauffeur",
            "chauffeurs",
            "chauffeuse",
            "conducteur",
            "conductora",
            "conductor",
            "fahrer",
            "fahrerin",
            "driver",
            "chofer",
        },
        ("chauffeur", "Fahrer", "conducteur", "driver", "Chauffeur"),
    ),
    _group(
        {
            "comptable",
            "comptables",
            "accountant",
            "accounting",
            "contable",
            "contabilista",
            "buchhalter",
            "buchhalterin",
            "comptabilite",
        },
        ("comptable", "accountant", "Buchhalter", "comptabilité"),
    ),
    _group(
        {
            "cuisinier",
            "cuisiniere",
            "cuisiniers",
            "cocinero",
            "cocinera",
            "cozinheiro",
            "cozinheira",
            "koch",
            "kochin",
            "chef",
            "cuisine",
        },
        ("cuisinier", "Koch", "chef", "cuisine", "Chef de partie"),
    ),
    _group(
        {
            "enseignant",
            "enseignante",
            "enseignants",
            "professeur",
            "professeure",
            "profesor",
            "profesora",
            "professor",
            "professora",
            "teacher",
            "lehrperson",
            "docent",
        },
        ("enseignant", "professeur", "teacher", "Lehrperson", "Professeur"),
    ),
    _group(
        {
            "vendeur",
            "vendeuse",
            "vendeurs",
            "vendedor",
            "vendedora",
            "verkaufer",
            "verkaeufer",
            "verkauferin",
            "verkaeuferin",
            "retail",
            "vente",
        },
        ("vendeur", "Verkäufer", "Verkauf", "vente", "commercial"),
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
