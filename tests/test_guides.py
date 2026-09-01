"""Public SEO guides — HTML, official links, no legal advice."""

import pytest
from fastapi.testclient import TestClient

from sentinel_suisse.guides import load_guide_markdown, render_guide_page, render_guides_index
from sentinel_suisse.main import create_app

ORIGIN = "https://linkswiss.ch"


def test_dossier_es_has_official_link_and_disclaimer() -> None:
    page = render_guide_page(slug="dossier", lang="es", origin=ORIGIN)
    assert "Dossier de piso" in page
    assert "www.ch.ch" in page
    assert "no es asesoría legal" in page.lower() or "no es asesoria legal" in page
    assert "Sentinela no es abogada" in page
    assert 'rel="canonical"' in page


def test_cv_and_permit_g_point_to_sem() -> None:
    cv = render_guide_page(slug="cv", lang="fr", origin=ORIGIN)
    permit = render_guide_page(slug="permis-g", lang="es", origin=ORIGIN)
    assert "sem.admin.ch" in cv
    assert "arbeit.swiss" in cv
    assert "sem.admin.ch" in permit
    assert "Ausweis" not in permit  # Spanish page
    assert "Permiso G" in permit


def test_unknown_guide_markdown_raises() -> None:
    with pytest.raises(ValueError, match="Unknown guide"):
        load_guide_markdown("visa-l", "es")


def test_guides_index_lists_three() -> None:
    index = render_guides_index(lang="es", origin=ORIGIN)
    assert "/guides/dossier?lang=es" in index
    assert "/guides/cv?lang=es" in index
    assert "/guides/permis-g?lang=es" in index


def test_http_unknown_slug_is_404() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/guides/visa-l")
        assert response.status_code == 404


def test_http_dossier_ok() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/guides/dossier?lang=es")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "ch.ch" in response.text
        assert "Sentinela no es abogada" in response.text
