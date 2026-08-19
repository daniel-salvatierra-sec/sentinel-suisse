"""Add users.free_alerts_grandfathered — cut off free-tier alerts for new signups.

Existing users (as of this migration) keep their free email/WhatsApp alerts;
new signups going forward only get free search, and need Premium to receive
automatic alerts.

Revision ID: 011
Revises: 010
Create Date: 2026-08-19
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "011"
down_revision: str | None = "010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "free_alerts_grandfathered",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )
    # Existing rows are backfilled to True by server_default above. New rows created
    # after this point should default to False (no free alerts), so drop the default.
    op.alter_column("users", "free_alerts_grandfathered", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "free_alerts_grandfathered")
