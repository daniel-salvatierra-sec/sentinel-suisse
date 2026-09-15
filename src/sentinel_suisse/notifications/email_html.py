"""Build a simple HTML alternative for plain-text transactional emails.

Some mail clients (notably Outlook/Hotmail) don't reliably auto-linkify
long tokenized URLs in plain-text bodies, leaving users with a dead-looking
grey link they have to copy/paste by hand. Sending a `text/html` alternative
alongside the plain-text body guarantees a real clickable `<a>` tag.
"""

from __future__ import annotations

import re
from html import escape

_URL_RE = re.compile(r"https?://[^\s<]+")


def _clean_url(raw: str) -> str:
    return raw.rstrip(".,);")


def build_html_email(body: str, url: str | None = None) -> str:
    """Turn a plain-text email body into HTML, wrapping URLs in `<a>` tags."""
    urls: list[str] = []
    if url:
        urls.append(_clean_url(url))
    for found in _URL_RE.findall(body):
        cleaned = _clean_url(found)
        if cleaned not in urls:
            urls.append(cleaned)

    escaped_body = escape(body)
    for raw in urls:
        escaped_url = escape(raw)
        if escaped_url not in escaped_body:
            continue
        link = (
            f'<a href="{escaped_url}" style="color:#2563eb;word-break:break-all;">'
            f"{escaped_url}</a>"
        )
        escaped_body = escaped_body.replace(escaped_url, link)

    html_body = escaped_body.replace("\n", "<br>")
    return (
        "<!DOCTYPE html><html><body "
        'style="font-family:-apple-system,Segoe UI,Roboto,sans-serif;'
        'font-size:15px;line-height:1.5;color:#111827;">'
        f"{html_body}"
        "</body></html>"
    )
