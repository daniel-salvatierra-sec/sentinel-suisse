"""Geneva location alias expansion."""

from sentinel_suisse.services.location_match import expand_location_query, location_matches


def test_geneva_query_expands_to_suburbs() -> None:
    terms = expand_location_query("Genève")
    assert "Acacias" in terms
    assert "1227" in terms


def test_lausanne_expands_aliases() -> None:
    terms = expand_location_query("Lausanne")
    assert "Lausanne" in terms
    assert "Losanna" in terms


def test_zurich_and_airport_aliases() -> None:
    terms = expand_location_query("ZRH")
    assert "Zurich" in terms
    assert "Kloten" in terms
    assert location_matches("Kloten, Zurich", "Zürich") is True
    assert location_matches("Bern", "Zurich") is False


def test_bern_and_basel_aliases() -> None:
    assert "Berne" in expand_location_query("Berna")
    assert "Bâle" in expand_location_query("Basel")


def test_location_matches_suburb_for_geneva() -> None:
    assert location_matches("Châtelaine, 1219", "Geneva") is True
    assert location_matches("Lausanne, 1003", "Geneva") is False
