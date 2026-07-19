"""Add listing country for CH/FR zone filter.

Revision ID: 007
Revises: 006
Create Date: 2026-07-19
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "007"
down_revision: str | None = "006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

country_code_enum = postgresql.ENUM("CH", "FR", name="country_code", create_type=False)


def upgrade() -> None:
    country_code_enum.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "listings",
        sa.Column("country", country_code_enum, nullable=False, server_default="CH"),
    )
    op.alter_column("listings", "country", server_default=None)
    op.create_index("ix_listings_country", "listings", ["country"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_listings_country", table_name="listings")
    op.drop_column("listings", "country")
    country_code_enum.drop(op.get_bind(), checkfirst=True)
