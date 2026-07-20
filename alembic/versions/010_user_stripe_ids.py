"""Add Stripe customer/subscription ids on users.

Revision ID: 010
Revises: 009
Create Date: 2026-07-20
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "010"
down_revision: str | None = "009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("stripe_customer_id", sa.String(length=255), nullable=True))
    op.add_column(
        "users", sa.Column("stripe_subscription_id", sa.String(length=255), nullable=True)
    )
    op.create_index("ix_users_stripe_customer_id", "users", ["stripe_customer_id"], unique=False)
    op.create_index(
        "ix_users_stripe_subscription_id", "users", ["stripe_subscription_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_users_stripe_subscription_id", table_name="users")
    op.drop_index("ix_users_stripe_customer_id", table_name="users")
    op.drop_column("users", "stripe_subscription_id")
    op.drop_column("users", "stripe_customer_id")
