"""Add listings.is_hidden so the operator can take spam off search without deleting.

Revision ID: 013
Revises: 012
Create Date: 2026-08-21
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "013"
down_revision: str | None = "012"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "listings",
        sa.Column("is_hidden", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.alter_column("listings", "is_hidden", server_default=None)


def downgrade() -> None:
    op.drop_column("listings", "is_hidden")
