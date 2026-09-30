"""Expand job-word searches so Spanish/French queries match CH titles."""

from __future__ import annotations

import unicodedata


def _fold(value: str) -> str:
    normalized = unicodedata.normalize("NFD", value.strip().casefold())
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")


def _group(
    aliases: set[str],
    needles: tuple[str, ...],
    *,
    category: str = "",
    rejects: tuple[str, ...] = (),
) -> tuple[frozenset[str], tuple[str, ...], str, tuple[str, ...]]:
    return frozenset(_fold(item) for item in aliases), needles, category, rejects


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
        category="florist",
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
        category="cashier",
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
        ("infirmier", "infirmière", "Pflegefach", "Krankenpfleger", "Krankenschwester"),
        category="nursing",
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
            "programmeur",
            "programador",
            "informaticien",
        ),
        category="software",
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
        category="transport",
        # "conducteur" also names site managers and press operators.
        rejects=(
            "conducteur%travaux",
            "conducteur%chantier",
            "conducteur%machine",
            "conducteur%impression",
        ),
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
        category="accounting",
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
        ("cuisinier", "cuisinière", "Koch", "Köchin", "chef de cuisine", "chef de partie"),
        category="kitchen",
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
        category="teaching",
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
        ("vendeur", "vendeuse", "Verkäufer", "Verkäuferin"),
        category="retail",
    ),
    _group(
        {
            "limpieza",
            "limpiador",
            "limpiadora",
            "nettoyage",
            "nettoyeur",
            "nettoyeuse",
            "femme de menage",
            "agent de nettoyage",
            "agente de limpieza",
            "cleaning",
            "cleaner",
            "cleaners",
            "reinigung",
            "reinigungskraft",
            "putzkraft",
            "putzfrau",
            "limpeza",
            "faxineiro",
            "faxineira",
        },
        (
            "nettoyage",
            "Reinigung",
            "Reinigungskraft",
            "Putzkraft",
            "cleaning",
            "limpieza",
            "limpeza",
        ),
        category="cleaner",
    ),
    _group(
        {
            "conserje",
            "conserjeria",
            "conserjería",
            "concierge",
            "conciergerie",
            "hauswart",
            "abwart",
            "gardien d immeuble",
            "portero",
            "porteiro",
            "portaria",
        },
        (
            "concierge",
            "Hauswart",
            "Abwart",
            "gardien d",
            "conserje",
            "porteiro",
        ),
        category="concierge",
    ),
)


def _matching_group(query: str):
    folded = _fold(query)
    if not folded:
        return None
    for aliases, needles, category, rejects in _JOB_TERM_GROUPS:
        if folded in aliases:
            return aliases, needles, category, rejects
    return None


def is_occupation_query(query: str) -> bool:
    """True when the whole box is an occupation word, not "chofer Zurich"."""
    return _matching_group(query) is not None


def expand_text_query(query: str) -> list[str]:
    """Needles for title ILIKE. Unknown words stay as typed."""
    stripped = query.strip()
    if not stripped:
        return []
    group = _matching_group(stripped)
    if group is not None:
        return list(group[1])
    return [stripped]


def title_has_reject(title: str | None, query: str) -> bool:
    """True when a title matches an occupation false-positive pattern (`%` = anything)."""
    if not title:
        return False
    hay = title.casefold()
    for pattern in occupation_title_rejects(query):
        parts = [part.casefold() for part in pattern.split("%") if part]
        start = 0
        matched = bool(parts)
        for part in parts:
            found = hay.find(part, start)
            if found < 0:
                matched = False
                break
            start = found + len(part)
        if matched:
            return True
    return False


def occupation_title_rejects(query: str) -> tuple[str, ...]:
    group = _matching_group(query)
    if group is None:
        return ()
    return group[3]


def occupation_category(query: str) -> str | None:
    group = _matching_group(query)
    if group is None or not group[2]:
        return None
    return group[2]


_QUERY_STOPWORDS = frozenset(
    {
        "near",
        "the",
        "and",
        "for",
        "job",
        "jobs",
        "wie",
        "als",
        "bei",
        "pour",
        "avec",
        "dans",
        "pres",
        "proche",
        "und",
        "der",
        "die",
        "das",
        "un",
        "une",
        "des",
        "les",
        "los",
        "las",
        "con",
        "por",
        "para",
        "like",
        "similar",
        "ahnliche",
    }
)


def occupation_tokens(query: str) -> list[str]:
    """Occupation words inside a longer search, e.g. conducteur in 'TPG conducteur'."""
    folded = _fold(query)
    if not folded:
        return []
    found: list[str] = []
    for token in folded.split():
        if _matching_group(token) is not None and token not in found:
            found.append(token)
    return found


def _title_hits_needles(title: str, needles: list[str]) -> bool:
    hay = title.casefold()
    return any(needle.casefold() in hay for needle in needles)


def title_matches_job_query(title: str | None, query: str) -> bool:
    """True when the title is the occupation the person typed, not a nearby other job."""
    tokens = occupation_tokens(query)
    if not tokens:
        if not is_occupation_query(query):
            return False
        tokens = [_fold(query)]
    if not title:
        return False
    for token in tokens:
        if not _title_hits_needles(title, expand_text_query(token)):
            return False
        if title_has_reject(title, token):
            return False
    return True


def required_extra_terms(query: str) -> list[str]:
    """Non-occupation words that must still appear, e.g. TPG in 'TPG conducteur'."""
    from sentinel_suisse.services.location_match import expand_location_query

    folded = _fold(query)
    roles = set(occupation_tokens(query))
    terms: list[str] = []
    for token in folded.split():
        if len(token) < 3 or token in roles or token in _QUERY_STOPWORDS:
            continue
        if expand_location_query(token) != [token]:
            continue
        if token not in terms:
            terms.append(token)
    return terms


def query_looks_like_job(query: str) -> bool:
    folded = _fold(query)
    if not folded:
        return False
    for aliases, _needles, _category, _rejects in _JOB_TERM_GROUPS:
        if folded in aliases:
            return True
        if any(token in aliases for token in folded.split()):
            return True
    return False
