"""Add unique constraint on alerts_log to prevent duplicate alerts.

Revision ID: 003
Revises: 002
Create Date: 2026-07-11
"""

from collections.abc import Sequence

from alembic import op

revision: str = "003"
down_revision: str | None = "002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_alert_user_search_listing",
        "alerts_log",
        ["user_id", "saved_search_id", "listing_id"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_alert_user_search_listing", "alerts_log", type_="unique")
