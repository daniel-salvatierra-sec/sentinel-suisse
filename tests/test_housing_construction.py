from sentinel_suisse.models.enums import ListingType
from sentinel_suisse.services.housing_construction import (
    resolve_under_construction,
    text_looks_under_construction,
)


def test_new_project_phrases_match() -> None:
    assert text_looks_under_construction("Erstvermietung 3.5 Zimmer Genève", None) is True
    assert text_looks_under_construction("Projet neuf à la location — Lancy", None) is True
    assert text_looks_under_construction("Neubau 4.5 Zimmer, bezugsbereit", None) is True
    assert text_looks_under_construction(None, "Première location dans immeuble neuf") is True
    assert text_looks_under_construction("Promotion immobilière — 12 logements", None) is True


def test_off_plan_and_still_building_do_not_match() -> None:
    assert text_looks_under_construction("3.5 pièces en construction", None) is False
    assert text_looks_under_construction("Wohnung im Bau", None) is False
    assert text_looks_under_construction("Vente sur plan à Sion", None) is False
    assert text_looks_under_construction(None, "Livraison prévue 2027") is False
    assert text_looks_under_construction("Loft en obra", None) is False


def test_generic_renovated_neuf_does_not_match() -> None:
    assert text_looks_under_construction("Appartement neuf rénové", None) is False
    assert text_looks_under_construction("Baumgartenweg 5, Birsfelden", None) is False


def test_resolve_backfills_from_text() -> None:
    assert (
        resolve_under_construction(
            listing_type=ListingType.HOUSING,
            title="Projet neuf — première location",
            description=None,
            flagged=None,
        )
        is True
    )


def test_off_plan_text_overrides_flag() -> None:
    assert (
        resolve_under_construction(
            listing_type=ListingType.HOUSING,
            title="Appartement sur plan",
            description=None,
            flagged=True,
        )
        is False
    )


def test_jobs_are_not_inferred_from_text() -> None:
    assert (
        resolve_under_construction(
            listing_type=ListingType.JOB,
            title="Chef de chantier — projet neuf",
            description=None,
            flagged=None,
        )
        is None
    )


def test_payload_new_building_flag() -> None:
    assert (
        resolve_under_construction(
            listing_type=ListingType.HOUSING,
            title="Apartment",
            description=None,
            flagged=None,
            payload={"is_new_building": True},
        )
        is True
    )


def test_payload_off_plan_flag_does_not_match() -> None:
    assert (
        resolve_under_construction(
            listing_type=ListingType.HOUSING,
            title="Apartment",
            description=None,
            flagged=None,
            payload={"is_off_plan": True},
        )
        is False
    )
