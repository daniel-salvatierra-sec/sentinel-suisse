from sqlalchemy import select
from sqlalchemy.dialects import postgresql

from sentinel_suisse.models.listing import Listing
from sentinel_suisse.schemas.search import SearchQuery
from sentinel_suisse.services.search import _apply_filters


def _sql(location: str) -> str:
    stmt = _apply_filters(select(Listing.id), SearchQuery(location=location))
    return str(stmt.compile(dialect=postgresql.dialect())).lower()


def test_city_search_sql_does_not_scan_titles() -> None:
    sql = _sql("Sion")
    assert "location" in sql
    assert "title" not in sql
    assert "description" not in sql


def test_occupation_search_sql_still_scans_titles() -> None:
    sql = _sql("fleuriste")
    assert "title" in sql
    assert "description" in sql
