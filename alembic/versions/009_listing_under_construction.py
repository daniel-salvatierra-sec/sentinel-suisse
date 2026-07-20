"""Add listings.is_under_construction for off-plan / construction housing.

Revision ID: 009
Revises: 008
Create Date: 2026-07-20
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "009"
down_revision: str | None = "008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "listings",
        sa.Column("is_under_construction", sa.Boolean(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("listings", "is_under_construction")
