"""Add listings.is_featured + featured_until for paid boost.

Revision ID: 015
Revises: 014
Create Date: 2026-08-27
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "015"
down_revision: str | None = "014"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "listings",
        sa.Column("is_featured", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "listings",
        sa.Column("featured_until", sa.DateTime(timezone=True), nullable=True),
    )
    op.alter_column("listings", "is_featured", server_default=None)
    op.create_index(
        "ix_listings_featured_until",
        "listings",
        ["is_featured", "featured_until"],
    )


def downgrade() -> None:
    op.drop_index("ix_listings_featured_until", table_name="listings")
    op.drop_column("listings", "featured_until")
    op.drop_column("listings", "is_featured")
