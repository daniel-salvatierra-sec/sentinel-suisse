"""Dispatch alerts for a listing (pilot: console notifier)."""

import argparse
import logging
import sys

from sentinel_suisse.db.session import SessionLocal
from sentinel_suisse.services.alerts import AlertService

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")


def main() -> None:
    parser = argparse.ArgumentParser(description="Dispatch alerts for a listing")
    parser.add_argument("--listing-id", type=int, required=True, help="Listing ID to evaluate")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        stats = AlertService(db).dispatch_for_listing(args.listing_id)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()

    print(
        f"Dispatch complete for listing_id={args.listing_id}\n"
        f"  matched={stats.matched} sent={stats.sent} "
        f"skipped={stats.skipped} failed={stats.failed}"
    )


if __name__ == "__main__":
    main()
