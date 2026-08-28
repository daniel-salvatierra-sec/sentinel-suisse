"""Extract embedded JSON bootstrap state from portal HTML pages."""

import json
import re
from typing import Any

_LD_JSON_OPEN_RE = re.compile(r'<script[^>]*type="application/ld\+json"[^>]*>', re.IGNORECASE)


class EmbedParseError(RuntimeError):
    """Embedded JSON state was not found or is invalid."""


def extract_embedded_object(html: str, marker: str) -> dict[str, Any]:
    idx = html.find(marker)
    if idx == -1:
        msg = f"Embedded marker not found: {marker}"
        raise EmbedParseError(msg)
    json_start = idx + len(marker)
    try:
        state, _end = json.JSONDecoder().raw_decode(html, json_start)
    except json.JSONDecodeError as exc:
        msg = f"Invalid JSON after marker: {marker}"
        raise EmbedParseError(msg) from exc
    if not isinstance(state, dict):
        msg = f"Embedded state must be a JSON object ({marker})"
        raise EmbedParseError(msg)
    return state


def extract_first_state(html: str, markers: tuple[str, ...]) -> dict[str, Any]:
    last_error: EmbedParseError | None = None
    for marker in markers:
        try:
            return extract_embedded_object(html, marker)
        except EmbedParseError as exc:
            last_error = exc
    msg = "No supported embedded state marker found in HTML"
    if last_error is not None:
        raise EmbedParseError(msg) from last_error
    raise EmbedParseError(msg)


def extract_json_ld_job_postings(html: str) -> list[dict[str, Any]]:
    """Parse schema.org JobPosting entries from the search page JSON-LD block."""
    match = _LD_JSON_OPEN_RE.search(html)
    if not match:
        msg = "JSON-LD script block not found in HTML"
        raise EmbedParseError(msg)
    json_start = match.end()
    while json_start < len(html) and html[json_start].isspace():
        json_start += 1
    try:
        blocks, _end = json.JSONDecoder().raw_decode(html, json_start)
    except json.JSONDecodeError as exc:
        msg = "Invalid JSON-LD script block"
        raise EmbedParseError(msg) from exc
    if not isinstance(blocks, list):
        msg = "JSON-LD root must be an array"
        raise EmbedParseError(msg)

    jobs: list[dict[str, Any]] = []
    for block in blocks:
        if not isinstance(block, dict):
            continue
        if block.get("@type") == "ItemList":
            for element in block.get("itemListElement", []):
                if not isinstance(element, dict):
                    continue
                item = element.get("item")
                if isinstance(item, dict) and item.get("@type") == "JobPosting":
                    jobs.append(item)
        elif block.get("@type") == "JobPosting":
            jobs.append(block)
    if not jobs:
        msg = "No JobPosting entries in JSON-LD"
        raise EmbedParseError(msg)
    return jobs
