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
    assert "Renens" in terms
    assert "Ecublens" in terms
    assert "1003" in terms
    assert location_matches("Renens VD", "Lausanne") is True
    assert location_matches("Mobi-Lausanne", "Lausanne") is True


def test_zurich_and_airport_aliases() -> None:
    terms = expand_location_query("ZRH")
    assert "Zurich" in terms
    assert "Kloten" in terms
    assert location_matches("Kloten, Zurich", "Zürich") is True
    assert location_matches("Bern", "Zurich") is False


def test_bern_and_basel_aliases() -> None:
    assert "Berne" in expand_location_query("Berna")
    assert "Bâle" in expand_location_query("Basel")


def test_more_swiss_city_aliases() -> None:
    assert "Luzern" in expand_location_query("Lucerne")
    assert "Saint-Gall" in expand_location_query("St. Gallen")
    assert "Bienne" in expand_location_query("Biel")
    assert "Sitten" in expand_location_query("Sion")
    assert location_matches("Luzern, Switzerland", "Lucerna") is True
    assert location_matches("Sion, VS", "Sion") is True
    assert location_matches("Lausanne", "Sion") is False
    assert location_matches("Caisse de pension, Lausanne", "Sion") is False
    assert location_matches("Fribourg", "Freiburg") is True


def test_smaller_swiss_town_aliases() -> None:
    assert "Yverdon-les-Bains" in expand_location_query("Yverdon")
    assert "Siders" in expand_location_query("Sierre")
    assert "Soleure" in expand_location_query("Solothurn")
    assert "Brigue" in expand_location_query("Brig")
    assert location_matches("Locarno, Ticino", "Locarno") is True
    assert location_matches("Delémont", "Delsberg") is True


def test_location_matches_suburb_for_geneva() -> None:
    assert location_matches("Châtelaine, 1219", "Geneva") is True
    assert location_matches("Lausanne, 1003", "Geneva") is False


def test_geneva_query_does_not_pull_french_border_towns() -> None:
    terms = expand_location_query("Geneva")
    assert "Annemasse" not in terms
    assert "Gaillard" not in terms
    assert location_matches("Annemasse, 74100", "Geneva") is False
    assert location_matches("Carouge, 1227", "Geneva") is True


def test_neighbor_border_queries_expand_to_border_towns() -> None:
    fr_terms = expand_location_query("FR-border")
    assert "Annemasse" in fr_terms
    assert "Annecy" in fr_terms
    assert location_matches("Annemasse, 74100", "FR-border") is True
    assert location_matches("Paris, Île-de-France", "FR-border") is False

    de_terms = expand_location_query("DE-border")
    assert "Konstanz" in de_terms
    assert location_matches("Weil am Rhein", "DE-border") is True
    assert location_matches("Berlin", "DE-border") is False

    it_terms = expand_location_query("IT-border")
    assert "Como" in it_terms
    assert location_matches("Varese, Lombardia", "IT-border") is True
    assert location_matches("Roma", "IT-border") is False


def test_named_border_city_is_a_border_place() -> None:
    from sentinel_suisse.services.location_match import is_border_place, resolve_search_location

    assert is_border_place("Annemasse") is True
    assert is_border_place("Annecy") is True
    assert is_border_place("Konstanz") is True
    assert is_border_place("Como") is True
    assert is_border_place("Geneva") is False
    assert is_border_place("Paris") is False
    assert resolve_search_location("FR", None) == "FR-border"
    assert resolve_search_location("CH", None) is None


def test_neighbor_city_aliases() -> None:
    assert "München" in expand_location_query("Munich")
    assert "Köln" in expand_location_query("Cologne")
    assert "Roma" in expand_location_query("Rome")
    assert "Milano" in expand_location_query("Milan")
    assert location_matches("München, Bayern", "Munich") is True
    assert location_matches("Roma, Lazio", "Rome") is True
    assert location_matches("Paris", "Lyon") is False
