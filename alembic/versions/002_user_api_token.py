"""Add api_token_hash to users for API key authentication.

Revision ID: 002
Revises: 001
Create Date: 2026-07-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: str | None = "001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("api_token_hash", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "api_token_hash")
