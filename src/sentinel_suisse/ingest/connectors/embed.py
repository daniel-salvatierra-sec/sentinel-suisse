"""Extract embedded JSON bootstrap state from portal HTML pages."""

import json
from typing import Any


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
