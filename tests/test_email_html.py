"""Tests for the plain-text-to-HTML email helper."""

from sentinel_suisse.notifications.email_html import build_html_email


def test_build_html_email_wraps_url_in_anchor() -> None:
    url = "https://linkswiss.ch/?login=abc.def"
    body = f"Bonjour,\n\nCliquez ici :\n\n{url}\n\nMerci."
    html = build_html_email(body, url)

    assert f'<a href="{url}"' in html
    assert "<br>" in html
    assert "Bonjour" in html


def test_build_html_email_wraps_every_https_url() -> None:
    app = "https://linkswiss.ch/?listing=42"
    source = "https://www.adzuna.ch/details/1?utm_medium=api&utm_source=x"
    body = f"Ouvrir:\n{app}\n\nOffre:\n{source}\n"
    html = build_html_email(body, app)

    assert f'<a href="{app}"' in html
    assert 'href="https://www.adzuna.ch/details/1?utm_medium=api&amp;utm_source=x"' in html


def test_build_html_email_escapes_unsafe_characters() -> None:
    url = "https://linkswiss.ch/?login=abc"
    body = f"<script>alert(1)</script> {url}"
    html = build_html_email(body, url)

    assert "<script>" not in html
    assert "&lt;script&gt;" in html
