"""Add user locale for localized alert templates.

Revision ID: 005
Revises: 004
Create Date: 2026-07-13
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "005"
down_revision: str | None = "004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("locale", sa.String(length=5), nullable=False, server_default="fr"),
    )
    op.alter_column("users", "locale", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "locale")
