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


def test_chef_stays_on_kitchen_titles() -> None:
    needles = [item.casefold() for item in expand_text_query("chef")]
    assert "cuisinier" in needles
    assert "chef" not in needles
    assert "cuisine" not in needles


def test_vendedor_stays_on_seller_titles() -> None:
    needles = [item.casefold() for item in expand_text_query("vendedor")]
    assert "vendeur" in needles
    assert "commercial" not in needles
    assert "vente" not in needles


def test_desarrollador_stays_on_developer_titles() -> None:
    needles = [item.casefold() for item in expand_text_query("desarrollador")]
    assert "developer" in needles
    assert "software" not in needles
    assert "informatique" not in needles


def test_chofer_expands_to_driver_titles() -> None:
    needles = expand_text_query("chofer")
    assert "chauffeur" in needles
    assert "Fahrer" in needles
    assert query_looks_like_job("chofer") is True


def test_city_query_stays_literal() -> None:
    assert expand_text_query("Geneva") == ["Geneva"]


def test_occupation_words_look_like_jobs() -> None:
    assert query_looks_like_job("floristeria") is True
    assert query_looks_like_job("cajero") is True
    assert query_looks_like_job("limpieza") is True
    assert query_looks_like_job("conserje") is True
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
        ("limpieza", "nettoyage"),
        ("conserje", "concierge"),
    ],
)
def test_common_occupation_queries_expand(query: str, needle: str) -> None:
    assert query_looks_like_job(query) is True
    assert needle in expand_text_query(query)
