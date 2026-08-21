"""Add listings.owner_user_id for landlord-posted housing, plus direct provider.

Revision ID: 012
Revises: 011
Create Date: 2026-08-21
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "012"
down_revision: str | None = "011"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("listings", sa.Column("owner_user_id", sa.Integer(), nullable=True))
    op.create_index("ix_listings_owner_user_id", "listings", ["owner_user_id"])
    op.create_foreign_key(
        "fk_listings_owner_user_id",
        "listings",
        "users",
        ["owner_user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.execute(
        sa.text(
            "INSERT INTO providers (name, slug, base_url, is_active) "
            "SELECT 'Direct', 'direct', 'https://linkswiss.ch', true "
            "WHERE NOT EXISTS (SELECT 1 FROM providers WHERE slug = 'direct')"
        )
    )


def downgrade() -> None:
    op.drop_constraint("fk_listings_owner_user_id", "listings", type_="foreignkey")
    op.drop_index("ix_listings_owner_user_id", table_name="listings")
    op.drop_column("listings", "owner_user_id")
    op.execute(sa.text("DELETE FROM providers WHERE slug = 'direct'"))
