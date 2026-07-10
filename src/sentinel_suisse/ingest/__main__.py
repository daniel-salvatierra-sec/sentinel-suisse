"""Ingestion CLI."""

import argparse
from pathlib import Path

from sentinel_suisse.db.session import SessionLocal
from sentinel_suisse.ingest.connectors.fixture import load_fixture
from sentinel_suisse.ingest.service import IngestService


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest listings into Sentinel Suisse")
    parser.add_argument(
        "--provider",
        required=True,
        help="Provider slug (e.g. homegate)",
    )
    parser.add_argument(
        "--fixture",
        type=Path,
        required=True,
        help="Path to JSON fixture file",
    )
    args = parser.parse_args()

    items = load_fixture(args.fixture)
    db = SessionLocal()
    try:
        stats = IngestService(db).upsert_listings(args.provider, items)
    finally:
        db.close()

    print(f"Ingest complete for provider={args.provider!r}")
    print(f"  created={stats.created} updated={stats.updated} skipped={stats.skipped}")


if __name__ == "__main__":
    main()
