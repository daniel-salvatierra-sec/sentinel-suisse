"""Job category hierarchy for matching (field ↔ branch) plus portal aliases."""

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
    "legal": "other",
    "creative": "other",
    "science": "other",
    "manufacturing": "other",
    "property": "other",
}

ALL_SLUGS: frozenset[str] = FIELD_SLUGS | frozenset(BRANCH_PARENT)

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
    ("warehouse", "logistics"),
    ("accounting", "admin"),
    ("consulting", "admin"),
    ("nursing", "healthcare"),
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


def _fold_category(value: str) -> str:
    cleaned = value.strip().casefold().replace("_", " ").replace("-", " ")
    return " ".join(cleaned.split())


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


def _related_job_categories(filter_category: str) -> set[str]:
    parent = BRANCH_PARENT.get(filter_category, filter_category)
    related: set[str] = {filter_category, parent}
    for branch, field in BRANCH_PARENT.items():
        if field == parent or field == filter_category:
            related.add(branch)
            related.add(field)
    return related


def _parent_field(slug: str) -> str:
    return BRANCH_PARENT.get(slug, slug)


def stored_job_category_values(filter_category: str) -> list[str]:
    """DB values that should match this UI filter (our slugs + portal aliases)."""
    canon = canonical_job_category(filter_category) or filter_category
    related = _related_job_categories(canon)
    values: set[str] = set(related)
    values.add(filter_category)
    for alias, slug in _ALIAS_TO_SLUG.items():
        if slug in related or _parent_field(slug) in related:
            values.add(alias)
            values.add(alias.replace("-", " "))
    # Common title-case Adzuna labels as stored today.
    for slug in list(related):
        values.add(f"{slug} jobs")
        values.add(f"{slug.title()} Jobs")
    return sorted(values)


def non_other_stored_values() -> list[str]:
    """Known strings that belong to a named field (not 'other')."""
    values: set[str] = set()
    for slug in ALL_SLUGS:
        if _parent_field(slug) == "other" or slug == "other":
            continue
        values.add(slug)
    for alias, slug in _ALIAS_TO_SLUG.items():
        if _parent_field(slug) == "other" or slug == "other":
            continue
        values.add(alias)
        values.add(alias.replace("-", " "))
        values.add(f"{slug.title()} Jobs")
    return sorted(values)


def job_category_matches(listing_category: str | None, filter_category: str | None) -> bool:
    """NULL-safe hierarchical match: same leaf, same field, or branch under field."""
    if filter_category is None:
        return True
    listing_canon = canonical_job_category(listing_category)
    filter_canon = canonical_job_category(filter_category) or filter_category
    if listing_canon is None:
        return _parent_field(filter_canon) == "other" or filter_canon == "other"
    if listing_canon == filter_canon:
        return True

    listing_field = _parent_field(listing_canon)
    filter_field = _parent_field(filter_canon)
    if listing_field == filter_field:
        return True
    if filter_canon == listing_field:
        return True
    if listing_canon == filter_field:
        return True
    return False
