from sqlalchemy import select
from sqlalchemy.dialects import postgresql

from sentinel_suisse.models.listing import Listing
from sentinel_suisse.schemas.search import SearchQuery
from sentinel_suisse.services.search import _apply_filters, _apply_sort


def test_price_asc_orders_nulls_last() -> None:
    sql = str(
        _apply_sort(select(Listing), "price_asc").compile(dialect=postgresql.dialect())
    ).lower()
    assert "listings.price" in sql
    assert "asc" in sql
    assert "nulls last" in sql


def test_newest_orders_by_fetched_at() -> None:
    sql = str(_apply_sort(select(Listing), "newest").compile(dialect=postgresql.dialect())).lower()
    assert "fetched_at" in sql
    assert "desc" in sql


def test_under_construction_filter_scans_new_project_text() -> None:
    stmt = _apply_filters(select(Listing.id), SearchQuery(is_under_construction=True))
    compiled = stmt.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True})
    sql = str(compiled).lower()
    assert "is_under_construction" in sql
    assert "projet neuf" in sql
    assert "erstvermietung" in sql
    assert "neubau" in sql
    assert "en construction" in sql  # excluded via NOT
    assert " not " in sql or "not (" in sql
