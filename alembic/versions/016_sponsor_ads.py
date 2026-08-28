"""Add sponsor_ads for manual advertising placements.

Revision ID: 016
Revises: 015
Create Date: 2026-08-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "016"
down_revision: str | None = "015"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "sponsor_ads",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sponsor_name", sa.String(length=120), nullable=False),
        sa.Column("placement", sa.String(length=32), nullable=False),
        sa.Column("context", sa.String(length=16), nullable=False),
        sa.Column("headline", sa.String(length=160), nullable=True),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column("target_url", sa.String(length=1000), nullable=False),
        sa.Column("monthly_chf", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("impression_count", sa.Integer(), nullable=False),
        sa.Column("click_count", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sponsor_ads_active", "sponsor_ads", ["is_active", "starts_at", "ends_at"])
    op.create_index("ix_sponsor_ads_context", "sponsor_ads", ["context"])


def downgrade() -> None:
    op.drop_index("ix_sponsor_ads_context", table_name="sponsor_ads")
    op.drop_index("ix_sponsor_ads_active", table_name="sponsor_ads")
    op.drop_table("sponsor_ads")
