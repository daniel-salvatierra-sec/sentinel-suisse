"""Load listings from a local JSON fixture (pilot connector)."""

import json
from pathlib import Path

from sentinel_suisse.ingest.schemas import RawListing


def load_fixture(path: Path) -> list[RawListing]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        msg = "Fixture must be a JSON array of listings"
        raise ValueError(msg)
    return [RawListing.model_validate(item) for item in data]
