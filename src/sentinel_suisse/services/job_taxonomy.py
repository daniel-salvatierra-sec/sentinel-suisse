"""Job category hierarchy for matching (field → branch → role) plus portal aliases."""

from __future__ import annotations

FIELD_SLUGS: frozenset[str] = frozenset(
    {
        "it",
        "healthcare",
        "construction",
        "hospitality",
        "admin",
        "finance",
        "sales",
        "education",
        "logistics",
        "watchmaking",
        "other",
    }
)

# branch → parent field (mirrors frontend jobTaxonomy)
BRANCH_PARENT: dict[str, str] = {
    "software": "it",
    "soc": "it",
    "data": "it",
    "network": "it",
    "support": "it",
    "nursing": "healthcare",
    "doctor": "healthcare",
    "therapy": "healthcare",
    "care": "healthcare",
    "pharma": "healthcare",
    "architecture": "construction",
    "civil": "construction",
    "engineering": "construction",
    "trades": "construction",
    "kitchen": "hospitality",
    "service": "hospitality",
    "hotel": "hospitality",
    "tourism": "hospitality",
    "hr": "admin",
    "office": "admin",
    "accounting": "admin",
    "consulting": "admin",
    "banking": "finance",
    "insurance": "finance",
    "fiduciary": "finance",
    "retail": "sales",
    "b2b": "sales",
    "customer": "sales",
    "teaching": "education",
    "social": "education",
    "public": "education",
    "warehouse": "logistics",
    "transport": "logistics",
    "purchasing": "logistics",
    "watchmaker": "watchmaking",
    "jewelry": "watchmaking",
    "microtech": "watchmaking",
    "aftersales": "watchmaking",
    "legal": "other",
    "creative": "other",
    "science": "other",
    "manufacturing": "other",
    "property": "other",
}

# role → parent branch (only where one specialty still covers many jobs)
ROLE_PARENT: dict[str, str] = {
    "bus": "transport",
    "truck": "transport",
    "delivery": "transport",
    "crane": "transport",
    "taxi": "transport",
    "hospital": "nursing",
    "homecare": "nursing",
    "geriatric": "nursing",
    "clinic": "nursing",
    "assembly": "watchmaker",
    "restoration": "watchmaker",
    "polishing": "watchmaker",
    "florist": "retail",
    "cashier": "retail",
}

IMMEDIATE_PARENT: dict[str, str] = {**BRANCH_PARENT, **ROLE_PARENT}

ALL_SLUGS: frozenset[str] = FIELD_SLUGS | frozenset(BRANCH_PARENT) | frozenset(ROLE_PARENT)

_CHILDREN: dict[str, tuple[str, ...]] = {}
for _child, _parent in IMMEDIATE_PARENT.items():
    _CHILDREN[_parent] = (*_CHILDREN.get(_parent, ()), _child)

# Folded Adzuna tags/labels (and similar ATS strings) → our slug.
_ALIAS_TO_SLUG: dict[str, str] = {
    "it-jobs": "it",
    "it jobs": "it",
    "admin-jobs": "admin",
    "admin jobs": "admin",
    "accounting-finance-jobs": "finance",
    "accounting finance jobs": "finance",
    "sales-jobs": "sales",
    "sales jobs": "sales",
    "customer-services-jobs": "sales",
    "customer services jobs": "sales",
    "pr-advertising-marketing-jobs": "sales",
    "pr advertising marketing jobs": "sales",
    "healthcare-nursing-jobs": "healthcare",
    "healthcare nursing jobs": "healthcare",
    "hospitality-catering-jobs": "hospitality",
    "hospitality catering jobs": "hospitality",
    "logistics-warehouse-jobs": "logistics",
    "logistics warehouse jobs": "logistics",
    "teaching-jobs": "education",
    "teaching jobs": "education",
    "trade-construction-jobs": "construction",
    "trade construction jobs": "construction",
    "engineering-jobs": "construction",
    "engineering jobs": "construction",
    "hr-jobs": "admin",
    "hr jobs": "admin",
    "consultancy-jobs": "admin",
    "consultancy jobs": "admin",
    "legal-jobs": "legal",
    "legal jobs": "legal",
    "creative-design-jobs": "creative",
    "creative design jobs": "creative",
    "scientific-qa-jobs": "science",
    "scientific qa jobs": "science",
    "manufacturing-jobs": "manufacturing",
    "manufacturing jobs": "manufacturing",
    "property-jobs": "property",
    "property jobs": "property",
    "social-work-jobs": "social",
    "social work jobs": "social",
    "energy-oil-gas-jobs": "other",
    "energy oil gas jobs": "other",
    "other-general-jobs": "other",
    "other general jobs": "other",
    "domestic-help-cleaning-jobs": "other",
    "domestic help cleaning jobs": "other",
    "maintenance-jobs": "trades",
    "maintenance jobs": "trades",
    "graduate-jobs": "other",
    "graduate jobs": "other",
    "part-time-jobs": "other",
    "part time jobs": "other",
    "travel-jobs": "tourism",
    "travel jobs": "tourism",
    "horlogerie": "watchmaking",
    "watchmaking": "watchmaking",
    "watch making": "watchmaking",
    "hospital and health care": "healthcare",
    "hospital and health": "healthcare",
}

# Longer needles first so "healthcare" wins over shorter tokens.
_KEYWORD_TO_SLUG: tuple[tuple[str, str], ...] = (
    ("informatique", "it"),
    ("information technology", "it"),
    ("healthcare", "healthcare"),
    ("hospital and health", "healthcare"),
    ("hospitality", "hospitality"),
    ("construction", "construction"),
    ("engineering", "construction"),
    ("logistics", "logistics"),
    ("warehouse", "warehouse"),
    ("accounting", "admin"),
    ("consulting", "admin"),
    ("nursing", "nursing"),
    ("teaching", "education"),
    ("education", "education"),
    ("insurance", "finance"),
    ("banking", "finance"),
    ("finance", "finance"),
    ("customer", "sales"),
    ("marketing", "sales"),
    ("software", "it"),
    ("property", "property"),
    ("legal", "legal"),
    ("manufacturing", "manufacturing"),
    ("creative", "creative"),
    ("science", "science"),
    ("pharma", "healthcare"),
    ("kitchen", "hospitality"),
    ("tourism", "hospitality"),
    ("sales", "sales"),
    ("admin", "admin"),
)

_UNCLASSIFIED = frozenset({"unknown", "unknown jobs", "n/a", "none"})

# Title needles (accent-folded) → most specific slug. Longer first.
_TITLE_TO_SLUG: tuple[tuple[str, str], ...] = (
    ("mecanicien horloger", "watchmaker"),
    ("horloger rhabilleur", "restoration"),
    ("rhabilleur", "restoration"),
    ("rhabillage", "restoration"),
    ("polisseur", "polishing"),
    ("habillage", "assembly"),
    ("horloger", "watchmaker"),
    ("horlogere", "watchmaker"),
    ("horlogerie", "watchmaking"),
    ("watchmaker", "watchmaker"),
    ("watchmaking", "watchmaking"),
    ("uhrmacher", "watchmaker"),
    ("cadranier", "microtech"),
    ("sertisseur", "jewelry"),
    ("joaillier", "jewelry"),
    ("bijoutier", "jewelry"),
    ("recette fonctionnelle", "software"),
    ("analyste test", "software"),
    ("data scientist", "data"),
    ("data engineer", "data"),
    ("developpeur", "software"),
    ("developer", "software"),
    ("informaticien", "it"),
    ("informatique", "it"),
    ("fullstack", "software"),
    ("full stack", "software"),
    ("frontend", "software"),
    ("backend", "software"),
    ("devops", "software"),
    ("cybersecurite", "soc"),
    ("cybersecurity", "soc"),
    ("software", "software"),
    ("soins a domicile", "homecare"),
    ("aide et soins a domicile", "homecare"),
    ("spitex", "homecare"),
    ("home care", "homecare"),
    ("altersheim", "geriatric"),
    ("maison de retraite", "geriatric"),
    ("geriatr", "geriatric"),
    ("kinesitherapeute", "therapy"),
    ("aide soignant", "care"),
    ("cabinet medical", "clinic"),
    ("cabinet infirmier", "clinic"),
    ("hopital", "hospital"),
    ("hospital", "hospital"),
    ("clinique", "clinic"),
    ("infirmier", "nursing"),
    ("infirmiere", "nursing"),
    ("soignant", "care"),
    ("medecin", "doctor"),
    ("nursing", "nursing"),
    ("paysagiste", "construction"),
    ("electricien", "trades"),
    ("electrotechnicien", "trades"),
    ("macon", "trades"),
    ("manoeuvre", "trades"),
    ("soudeur", "trades"),
    ("carrossier", "trades"),
    ("mecanicien", "trades"),
    ("charpentier", "trades"),
    ("etancheur", "trades"),
    ("comptable", "accounting"),
    ("administratif", "office"),
    ("assistant adv", "office"),
    ("gestionnaire de paie", "hr"),
    ("ressources humaines", "hr"),
    ("professeur", "teaching"),
    ("enseignant", "teaching"),
    ("educateur", "social"),
    ("commercial", "sales"),
    ("blumenfachverkaufer", "florist"),
    ("blumenfachverkaeufer", "florist"),
    ("fleuriste", "florist"),
    ("floristin", "florist"),
    ("fiorista", "florist"),
    ("florista", "florist"),
    ("florist", "florist"),
    ("caissiere-vendeuse", "cashier"),
    ("caissier-vendeur", "cashier"),
    ("caissiere", "cashier"),
    ("caissier", "cashier"),
    ("kassierin", "cashier"),
    ("kassierer", "cashier"),
    ("cashier", "cashier"),
    ("cajero", "cashier"),
    ("cajera", "cashier"),
    ("vendeur", "retail"),
    ("chauffeur de bus", "bus"),
    ("chauffeur bus", "bus"),
    ("conducteur de bus", "bus"),
    ("conducteur d autobus", "bus"),
    ("conducteur autobus", "bus"),
    ("conducteur de ligne", "bus"),
    ("chauffeur de ligne", "bus"),
    ("busfahrer", "bus"),
    ("bus driver", "bus"),
    ("kleinbus", "bus"),
    ("reisebus", "bus"),
    ("trolleybus", "bus"),
    ("autobus", "bus"),
    ("autocar", "bus"),
    ("car postal", "bus"),
    ("postauto", "bus"),
    ("carpostal", "bus"),
    ("tramway", "bus"),
    ("tramfahrer", "bus"),
    ("linienbus", "bus"),
    ("stadtbus", "bus"),
    ("tpg", "bus"),
    ("vbsh", "bus"),
    ("verkehrsbetriebe", "bus"),
    ("uber eats", "delivery"),
    ("ubereats", "delivery"),
    ("chauffeur de taxi", "taxi"),
    ("taxi driver", "taxi"),
    ("taxifahrer", "taxi"),
    ("chauffeur vtc", "taxi"),
    (" vtc", "taxi"),
    ("taxi", "taxi"),
    ("poids lourd", "truck"),
    ("poids lourds", "truck"),
    ("camionnette", "delivery"),
    ("camionneur", "truck"),
    ("camion", "truck"),
    ("lkw", "truck"),
    ("grutier", "crane"),
    ("gruista", "crane"),
    ("crane operator", "crane"),
    ("livreur", "delivery"),
    ("repartidor", "delivery"),
    ("coursier", "delivery"),
    ("kurier", "delivery"),
    ("delivery driver", "delivery"),
    ("magasinier", "warehouse"),
    ("cariste", "warehouse"),
    ("chauffeur", "transport"),
    ("chofer", "transport"),
    ("cuisinier", "kitchen"),
    ("serveur", "service"),
    ("hotelier", "hotel"),
    ("restauration", "hospitality"),
    ("fiduciaire", "fiduciary"),
    ("banque", "banking"),
)

# ILIKE needles for live search, keyed by the most specific slug.
TITLE_SEARCH_NEEDLES: dict[str, tuple[str, ...]] = {
    "it": (
        "%informatic%",
        "%informatique%",
    ),
    "software": (
        "%développeur%",
        "%developpeur%",
        "%developer%",
        "%software%",
        "%devops%",
        "%fullstack%",
        "%full-stack%",
        "%full stack%",
        "%frontend%",
        "%backend%",
        "%analyste test%",
        "%recette fonctionnelle%",
    ),
    "soc": (
        "%cybersécurité%",
        "%cybersecurite%",
        "%cybersecurity%",
        "%cyber %",
    ),
    "data": (
        "%data scientist%",
        "%data engineer%",
    ),
    "healthcare": ("%healthcare%",),
    "nursing": (
        "%infirmier%",
        "%infirmière%",
        "%nursing%",
    ),
    "hospital": (
        "%hôpital%",
        "%hopital%",
        "%hospital%",
    ),
    "homecare": (
        "%spitex%",
        "%domicile%",
        "%home care%",
    ),
    "geriatric": (
        "%gériatr%",
        "%geriatr%",
        "%altersheim%",
        "%ems %",
        "% ems%",
    ),
    "clinic": (
        "%clinique%",
        "%cabinet%",
        "%praxis%",
    ),
    "doctor": (
        "%médecin%",
        "%medecin%",
    ),
    "therapy": (
        "%kinésithérapeute%",
        "%kinesitherapeute%",
    ),
    "care": (
        "%aide soignant%",
        "%soignant%",
    ),
    "construction": ("%paysagiste%",),
    "trades": (
        "%électricien%",
        "%electricien%",
        "%électrotechnicien%",
        "%macon%",
        "%maçon%",
        "%manoeuvre%",
        "%manœuvre%",
        "%soudeur%",
        "%carrossier%",
        "%mécanicien%",
        "%mecanicien%",
        "%étancheur%",
        "%etancheur%",
    ),
    "admin": ("%administratif%",),
    "hr": (
        "%gestionnaire de paie%",
        "%ressources humaines%",
    ),
    "office": ("%assistant adv%",),
    "accounting": ("%comptable%",),
    "education": ("%éducation%",),
    "teaching": (
        "%professeur%",
        "%enseignant%",
    ),
    "social": (
        "%éducateur%",
        "%educateur%",
    ),
    "sales": ("%commercial%",),
    "retail": ("%vendeur%",),
    "florist": (
        "%florist%",
        "%fleuriste%",
        "%floristin%",
        "%fiorista%",
        "%florista%",
        "%blumenfach%",
    ),
    "cashier": (
        "%caissier%",
        "%cashier%",
        "%kassierer%",
        "%kassierin%",
        "%cajero%",
    ),
    "hospitality": ("%restauration%",),
    "kitchen": ("%cuisinier%",),
    "service": ("%serveur%",),
    "hotel": (
        "%hôtelier%",
        "%hotelier%",
    ),
    "logistics": (
        "%logisticien%",
        "%logistique%",
    ),
    "warehouse": (
        "%magasinier%",
        "%cariste%",
        "%entrepôt%",
        "%entrepot%",
    ),
    "transport": (
        "%chauffeur%",
        "%chofer%",
    ),
    "bus": (
        "%busfahrer%",
        "%bus driver%",
        "%chauffeur de bus%",
        "%conducteur de bus%",
        "%conducteur d'autobus%",
        "%conducteur autobus%",
        "%conducteur de ligne%",
        "%chauffeur de ligne%",
        "%autocar%",
        "%autobus%",
        "%kleinbus%",
        "%reisebus%",
        "%trolleybus%",
        "%car postal%",
        "%postauto%",
        "%carpostal%",
        "%tramway%",
        "%tramfahrer%",
        "%linienbus%",
        "%stadtbus%",
        "%tpg%",
        "%vbsh%",
        "%verkehrsbetriebe%",
    ),
    "taxi": (
        "%taxifahrer%",
        "%chauffeur de taxi%",
        "%taxi driver%",
        "%chauffeur vtc%",
        "% vtc%",
        "%taxi %",
        "% taxi%",
    ),
    "truck": (
        "%poids lourd%",
        "%poids-lourd%",
        "%camion%",
        "%lkw%",
    ),
    "delivery": (
        "%livreur%",
        "%repartidor%",
        "%coursier%",
        "%kurier%",
        "%delivery%",
    ),
    "crane": (
        "%grutier%",
        "%gruista%",
        "%crane%",
    ),
    "finance": ("%finance%",),
    "fiduciary": ("%fiduciaire%",),
    "banking": ("%banque%",),
    "watchmaking": (
        "%horlogerie%",
        "%watchmaking%",
    ),
    "watchmaker": (
        "%horloger%",
        "%horlogère%",
        "%watchmaker%",
        "%uhrmacher%",
    ),
    "assembly": ("%habillage%",),
    "restoration": (
        "%rhabilleur%",
        "%rhabillage%",
    ),
    "polishing": ("%polisseur%",),
    "jewelry": (
        "%sertisseur%",
        "%joaillier%",
        "%bijoutier%",
    ),
    "microtech": (
        "%cadranier%",
        "%microtechnique%",
    ),
}


def _fold_text(value: str) -> str:
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
        .replace("-", " ")
        .replace("_", " ")
    )


def _fold_category(value: str) -> str:
    return " ".join(_fold_text(value).split())


def canonical_job_category(value: str | None) -> str | None:
    """Map a portal label/tag or our slug to a canonical field/branch slug."""
    if value is None:
        return None
    stripped = value.strip()
    if not stripped:
        return None
    lower = stripped.casefold()
    if lower in ALL_SLUGS:
        return lower
    folded = _fold_category(stripped)
    if folded in _UNCLASSIFIED:
        return None
    if folded in ALL_SLUGS:
        return folded
    if lower in _ALIAS_TO_SLUG:
        return _ALIAS_TO_SLUG[lower]
    if folded in _ALIAS_TO_SLUG:
        return _ALIAS_TO_SLUG[folded]
    for needle, slug in _KEYWORD_TO_SLUG:
        if needle in folded:
            return slug
    return "other"


def classify_from_title(title: str | None) -> str | None:
    if not title or not title.strip():
        return None
    folded = _fold_category(title)
    for needle, slug in _TITLE_TO_SLUG:
        if needle in folded:
            return slug
    return None


def _depth(slug: str) -> int:
    depth = 0
    current = slug
    seen: set[str] = set()
    while current in IMMEDIATE_PARENT and current not in seen:
        seen.add(current)
        current = IMMEDIATE_PARENT[current]
        depth += 1
    return depth


def parent_field(slug: str) -> str:
    current = slug
    seen: set[str] = set()
    while current not in FIELD_SLUGS:
        parent = IMMEDIATE_PARENT.get(current)
        if parent is None or parent in seen:
            return current
        seen.add(current)
        current = parent
    return current


def descendants(slug: str) -> set[str]:
    found: set[str] = set()
    stack = list(_CHILDREN.get(slug, ()))
    while stack:
        node = stack.pop()
        if node in found:
            continue
        found.add(node)
        stack.extend(_CHILDREN.get(node, ()))
    return found


def _ancestors(slug: str) -> set[str]:
    found: set[str] = set()
    current = slug
    while current in IMMEDIATE_PARENT:
        parent = IMMEDIATE_PARENT[current]
        if parent in found:
            break
        found.add(parent)
        current = parent
    return found


def classify_job_category(portal: str | None, title: str | None) -> str | None:
    """Prefer a more specific title slug when the portal tag is coarse or wrong."""
    title_canon = classify_from_title(title)
    portal_canon = canonical_job_category(portal)
    if title_canon and title_canon != "other":
        if portal_canon in (None, "other"):
            return title_canon
        if parent_field(title_canon) == parent_field(portal_canon):
            return title_canon if _depth(title_canon) >= _depth(portal_canon) else portal_canon
        if portal_canon == "construction":
            return title_canon
        if parent_field(title_canon) in {"it", "education", "healthcare", "admin", "watchmaking"}:
            return title_canon
    return portal_canon or title_canon or "other"


def title_needles_for_filter(filter_category: str) -> list[str]:
    canon = canonical_job_category(filter_category) or filter_category
    related = _related_job_categories(canon)
    needles: list[str] = []
    for slug in related:
        needles.extend(TITLE_SEARCH_NEEDLES.get(slug, ()))
    return needles


def _related_job_categories(filter_category: str) -> set[str]:
    """Filter node plus descendants — never siblings."""
    return {filter_category} | descendants(filter_category)


def _parent_field(slug: str) -> str:
    return parent_field(slug)


def stored_job_category_values(filter_category: str) -> list[str]:
    """DB values that should match this UI filter (our slugs + portal aliases)."""
    canon = canonical_job_category(filter_category) or filter_category
    related = _related_job_categories(canon)
    values: set[str] = set(related)
    values.add(filter_category)
    for alias, slug in _ALIAS_TO_SLUG.items():
        if slug in related:
            values.add(alias)
            values.add(alias.replace("-", " "))
    for slug in list(related):
        values.add(f"{slug} jobs")
        values.add(f"{slug.title()} Jobs")
    return sorted(values)


def non_other_stored_values() -> list[str]:
    """Known strings that belong to a named field (not 'other')."""
    values: set[str] = set()
    for slug in ALL_SLUGS:
        if parent_field(slug) == "other" or slug == "other":
            continue
        values.add(slug)
    for alias, slug in _ALIAS_TO_SLUG.items():
        if parent_field(slug) == "other" or slug == "other":
            continue
        values.add(alias)
        values.add(alias.replace("-", " "))
        values.add(f"{slug.title()} Jobs")
    return sorted(values)


def job_category_matches(
    listing_category: str | None,
    filter_category: str | None,
    title: str | None = None,
) -> bool:
    """Match the filter slug or a more specific descendant — never siblings."""
    if filter_category is None:
        return True
    listing_canon = classify_job_category(listing_category, title)
    filter_canon = canonical_job_category(filter_category) or filter_category
    if listing_canon is None:
        return parent_field(filter_canon) == "other" or filter_canon == "other"
    if listing_canon == filter_canon:
        return True
    return filter_canon in _ancestors(listing_canon)
