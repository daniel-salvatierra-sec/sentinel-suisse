"""Build a simple HTML alternative for plain-text transactional emails.

Some mail clients (notably Outlook/Hotmail) don't reliably auto-linkify
long tokenized URLs in plain-text bodies, leaving users with a dead-looking
grey link they have to copy/paste by hand. Sending a `text/html` alternative
alongside the plain-text body guarantees a real clickable `<a>` tag.
"""

from __future__ import annotations

from html import escape


def build_html_email(body: str, url: str) -> str:
    """Turn a plain-text email body into HTML, with `url` as a real link."""
    escaped_url = escape(url)
    link = f'<a href="{escaped_url}" style="color:#2563eb;">{escaped_url}</a>'
    escaped_body = escape(body).replace(escaped_url, link)
    html_body = escaped_body.replace("\n", "<br>")
    return (
        "<!DOCTYPE html><html><body "
        'style="font-family:-apple-system,Segoe UI,Roboto,sans-serif;'
        'font-size:15px;line-height:1.5;color:#111827;">'
        f"{html_body}"
        "</body></html>"
    )
