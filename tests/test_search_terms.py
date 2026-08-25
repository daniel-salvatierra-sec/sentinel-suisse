import pytest

from sentinel_suisse.services.search_terms import expand_text_query, query_looks_like_job


def test_floristeria_expands_to_swiss_title_words() -> None:
    needles = expand_text_query("floristeria")
    assert "florist" in needles
    assert "fleuriste" in needles


def test_accented_floristeria_folds() -> None:
    word = "florister" + chr(0xED) + "a"
    needles = expand_text_query(word)
    assert "florist" in needles
    assert query_looks_like_job(word) is True


def test_fleuriste_expands_to_florist() -> None:
    needles = expand_text_query("fleuriste")
    assert "florist" in needles


def test_city_query_stays_literal() -> None:
    assert expand_text_query("Geneva") == ["Geneva"]


def test_occupation_words_look_like_jobs() -> None:
    assert query_looks_like_job("floristeria") is True
    assert query_looks_like_job("cajero") is True
    assert query_looks_like_job("Geneva") is False
    assert query_looks_like_job("Sion") is False
    assert query_looks_like_job("Lucerne") is False


@pytest.mark.parametrize(
    ("query", "needle"),
    [
        ("infirmier", "infirmier"),
        ("développeur", "développeur"),
        ("developpeur", "developpeur"),
        ("chauffeur", "chauffeur"),
        ("comptable", "comptable"),
        ("cuisinier", "cuisinier"),
        ("enseignant", "enseignant"),
        ("vendeur", "vendeur"),
        ("enfermero", "infirmier"),
        ("desarrollador", "developer"),
    ],
)
def test_common_occupation_queries_expand(query: str, needle: str) -> None:
    assert query_looks_like_job(query) is True
    assert needle in expand_text_query(query)
