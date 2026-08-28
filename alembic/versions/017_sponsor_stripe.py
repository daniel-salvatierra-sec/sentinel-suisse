"""Add Stripe self-serve fields to sponsor_ads.

Revision ID: 017
Revises: 016
Create Date: 2026-08-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "017"
down_revision: str | None = "016"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("sponsor_ads", sa.Column("owner_user_id", sa.Integer(), nullable=True))
    op.add_column(
        "sponsor_ads",
        sa.Column("stripe_checkout_id", sa.String(length=255), nullable=True),
    )
    op.create_foreign_key(
        "fk_sponsor_ads_owner_user_id",
        "sponsor_ads",
        "users",
        ["owner_user_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_sponsor_ads_stripe_checkout_id",
        "sponsor_ads",
        ["stripe_checkout_id"],
        unique=True,
    )
    op.create_index("ix_sponsor_ads_owner_user_id", "sponsor_ads", ["owner_user_id"])


def downgrade() -> None:
    op.drop_index("ix_sponsor_ads_owner_user_id", table_name="sponsor_ads")
    op.drop_index("ix_sponsor_ads_stripe_checkout_id", table_name="sponsor_ads")
    op.drop_constraint("fk_sponsor_ads_owner_user_id", "sponsor_ads", type_="foreignkey")
    op.drop_column("sponsor_ads", "stripe_checkout_id")
    op.drop_column("sponsor_ads", "owner_user_id")
