"""Hierarchical job category matching."""

from sentinel_suisse.services.job_taxonomy import job_category_matches


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
    assert job_category_matches(None, "nursing") is True
    assert job_category_matches("nursing", None) is True
