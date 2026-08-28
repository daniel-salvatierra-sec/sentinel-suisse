"""JSON-LD parsing for JobCloud search pages."""

from pathlib import Path

from sentinel_suisse.config import Settings
from sentinel_suisse.ingest.connectors.embed import extract_json_ld_job_postings
from sentinel_suisse.ingest.connectors.jobcloud import (
    build_search_url,
    employment_type_from_text,
    iter_search_urls,
    map_json_ld_job_posting,
    split_csv,
    workload_from_title,
)
from sentinel_suisse.models.enums import EmploymentType

_FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "jobcloud_ld_search.html"


def test_extract_json_ld_job_postings() -> None:
    html = _FIXTURE.read_text(encoding="utf-8")
    jobs = extract_json_ld_job_postings(html)
    assert len(jobs) == 1
    assert jobs[0]["title"].startswith("Magasinier")


def test_map_json_ld_job_posting() -> None:
    html = _FIXTURE.read_text(encoding="utf-8")
    job = extract_json_ld_job_postings(html)[0]
    listing = map_json_ld_job_posting(
        job,
        source="jobup",
        base_url="https://www.jobup.ch",
        default_detail_path="/fr/emplois/detail/{job_id}/",
    )
    assert listing is not None
    assert listing.external_id == "ld-job-001"
    assert listing.job_category == "warehouse"
    assert listing.workload_min == 80
    assert listing.workload_max == 100
    assert listing.employment_type == EmploymentType.PERMANENT


def test_workload_from_title() -> None:
    assert workload_from_title("Collaborateur vente 30%") == (30, 30)
    assert workload_from_title("Engineer 80-100%") == (80, 100)


def test_employment_type_from_french_label() -> None:
    assert employment_type_from_text("Durée indéterminée") == EmploymentType.PERMANENT
    assert employment_type_from_text("Temporaire") == EmploymentType.TEMPORARY


def test_build_search_url() -> None:
    url = build_search_url(
        "https://www.jobup.ch",
        "/fr/emplois/",
        location="Genève",
        term="magasinier",
        page=2,
    )
    assert url.startswith("https://www.jobup.ch/fr/emplois/?")
    assert "location=Gen" in url
    assert "term=magasinier" in url
    assert "page=2" in url


def test_iter_search_urls_counts() -> None:
    settings = Settings(jobcloud_max_pages=2, jobcloud_role_keywords="magasinier,cariste")
    urls = list(
        iter_search_urls(
            settings,
            base_url="https://www.jobup.ch",
            search_path="/fr/emplois/",
            locations_csv="Genève,Zurich",
            role_locations_csv="Genève",
        )
    )
    # 2 cities * 2 pages + 1 city * 2 role terms
    assert len(urls) == 6
    assert split_csv("a, b,a") == ["a", "b"]
