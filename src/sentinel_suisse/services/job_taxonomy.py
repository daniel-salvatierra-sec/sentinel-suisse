"""Job category hierarchy for matching (field ↔ branch)."""

from __future__ import annotations

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
}


def job_category_matches(listing_category: str | None, filter_category: str | None) -> bool:
    """NULL-safe hierarchical match: same leaf, same field, or branch under field."""
    if filter_category is None:
        return True
    if listing_category is None:
        return True
    if listing_category == filter_category:
        return True

    listing_field = BRANCH_PARENT.get(listing_category, listing_category)
    filter_field = BRANCH_PARENT.get(filter_category, filter_category)
    if listing_field == filter_field:
        return True
    # Filter is a field, listing is a branch under it
    if filter_category == listing_field:
        return True
    # Filter is a branch, listing is the parent field
    if listing_category == filter_field:
        return True
    return False
