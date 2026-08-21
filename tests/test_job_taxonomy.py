"""Hierarchical job category matching."""

from sentinel_suisse.services.job_taxonomy import (
    canonical_job_category,
    classify_job_category,
    job_category_matches,
)


def test_same_leaf() -> None:
    assert job_category_matches("nursing", "nursing") is True


def test_branch_matches_parent_field() -> None:
    assert job_category_matches("nursing", "healthcare") is True
    assert job_category_matches("healthcare", "nursing") is True


def test_siblings_same_field() -> None:
    assert job_category_matches("nursing", "doctor") is True
    assert job_category_matches("soc", "software") is True


def test_different_fields() -> None:
    assert job_category_matches("nursing", "architecture") is False
    assert job_category_matches("it", "healthcare") is False


def test_null_safe() -> None:
    assert job_category_matches(None, "nursing") is False
    assert job_category_matches("nursing", None) is True
    assert job_category_matches(None, "other") is True


def test_adzuna_labels_map_to_fields() -> None:
    assert canonical_job_category("IT Jobs") == "it"
    assert canonical_job_category("it-jobs") == "it"
    assert job_category_matches("IT Jobs", "it") is True
    assert job_category_matches("Admin Jobs", "it") is False
    assert job_category_matches("Legal Jobs", "other") is True
    assert canonical_job_category("Développement informatique") == "it"


def test_unknown_adzuna_tag_uses_job_title() -> None:
    assert canonical_job_category("Unknown") is None
    assert classify_job_category("Unknown", "Développeur Full Stack") == "it"
    assert (
        classify_job_category("engineering-jobs", "Analyste Test / Recette fonctionnelle") == "it"
    )
    assert classify_job_category("Unknown", "Carrossier / Mécanicien") == "construction"
    assert classify_job_category("Unknown", "Collaborateur comptable autonome") == "admin"
    assert classify_job_category(None, "Paysagiste (H/F)") == "construction"
