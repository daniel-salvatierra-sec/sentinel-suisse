"""Add users.is_premium for freemium stub.

Revision ID: 008
Revises: 007
Create Date: 2026-07-20
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "008"
down_revision: str | None = "007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("is_premium", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.alter_column("users", "is_premium", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "is_premium")
