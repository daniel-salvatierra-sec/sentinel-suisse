from sentinel_suisse.models.enums import ListingType
from sentinel_suisse.services.housing_construction import (
    resolve_under_construction,
    text_looks_under_construction,
)


def test_explicit_phrases_match() -> None:
    assert text_looks_under_construction("3.5 pièces en construction", None) is True
    assert text_looks_under_construction("Wohnung im Bau", None) is True
    assert text_looks_under_construction("Vente sur plan à Sion", None) is True
    assert text_looks_under_construction(None, "Livraison prévue 2027") is True


def test_finished_neubau_does_not_match() -> None:
    assert text_looks_under_construction("Neubau 4.5 Zimmer, bezugsbereit", None) is False
    assert text_looks_under_construction("Appartement neuf rénové", None) is False


def test_resolve_backfills_from_text() -> None:
    assert (
        resolve_under_construction(
            listing_type=ListingType.HOUSING,
            title="Loft en obra",
            description=None,
            flagged=None,
        )
        is True
    )


def test_jobs_are_not_inferred_from_text() -> None:
    assert (
        resolve_under_construction(
            listing_type=ListingType.JOB,
            title="Chef de chantier en construction",
            description=None,
            flagged=None,
        )
        is None
    )


def test_payload_off_plan_flag() -> None:
    assert (
        resolve_under_construction(
            listing_type=ListingType.HOUSING,
            title="Apartment",
            description=None,
            flagged=None,
            payload={"is_off_plan": True},
        )
        is True
    )


def test_new_building_flag_alone_is_not_construction() -> None:
    assert (
        resolve_under_construction(
            listing_type=ListingType.HOUSING,
            title="Apartment",
            description=None,
            flagged=None,
            payload={"is_new_building": True},
        )
        is None
    )
