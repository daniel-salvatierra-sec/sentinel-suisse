"""Geneva location alias expansion."""

from sentinel_suisse.services.location_match import expand_location_query, location_matches


def test_geneva_query_expands_to_suburbs() -> None:
    terms = expand_location_query("Genève")
    assert "Acacias" in terms
    assert "1227" in terms


def test_lausanne_stays_literal() -> None:
    assert expand_location_query("Lausanne") == ["Lausanne"]


def test_location_matches_suburb_for_geneva() -> None:
    assert location_matches("Châtelaine, 1219", "Geneva") is True
    assert location_matches("Lausanne, 1003", "Geneva") is False
