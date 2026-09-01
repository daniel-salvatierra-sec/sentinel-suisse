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


def test_infirmier_search_sql_scans_titles() -> None:
    sql = _sql("infirmier")
    assert "title" in sql
    assert "description" in sql


def test_housing_border_sql_does_not_require_country() -> None:
    from sentinel_suisse.models.enums import CountryCode, ListingType

    stmt = _apply_filters(
        select(Listing.id),
        SearchQuery(
            listing_type=ListingType.HOUSING,
            location="FR-border",
            country=CountryCode.FR,
        ),
    )
    sql = str(
        stmt.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True})
    ).lower()
    assert "annemasse" in sql
    assert "listings.country" not in sql


def test_job_border_sql_does_not_require_country() -> None:
    from sentinel_suisse.models.enums import CountryCode, ListingType

    stmt = _apply_filters(
        select(Listing.id),
        SearchQuery(
            listing_type=ListingType.JOB,
            location="FR-border",
            country=CountryCode.FR,
        ),
    )
    sql = str(stmt.compile(dialect=postgresql.dialect())).lower()
    assert "listings.country" not in sql


def test_switzerland_sql_excludes_neighbor_border_towns() -> None:
    from sentinel_suisse.models.enums import CountryCode

    stmt = _apply_filters(select(Listing.id), SearchQuery(country=CountryCode.CH))
    sql = str(
        stmt.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True})
    ).lower()
    assert "annemasse" in sql
    assert "listings.country" in sql
    assert " not " in sql or "not (" in sql
