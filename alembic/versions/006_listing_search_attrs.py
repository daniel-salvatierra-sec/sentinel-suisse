"""Add housing/job search attributes on listings.

Revision ID: 006
Revises: 005
Create Date: 2026-07-18
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "006"
down_revision: str | None = "005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

property_type_enum = postgresql.ENUM(
    "studio",
    "apartment",
    "house",
    "room",
    "other",
    name="property_type",
    create_type=False,
)
employment_type_enum = postgresql.ENUM(
    "permanent",
    "temporary",
    "internship",
    "freelance",
    "other",
    name="employment_type",
    create_type=False,
)


def upgrade() -> None:
    property_type_enum.create(op.get_bind(), checkfirst=True)
    employment_type_enum.create(op.get_bind(), checkfirst=True)

    op.add_column("listings", sa.Column("rooms", sa.Numeric(precision=3, scale=1), nullable=True))
    op.add_column("listings", sa.Column("property_type", property_type_enum, nullable=True))
    op.add_column("listings", sa.Column("has_parking", sa.Boolean(), nullable=True))
    op.add_column("listings", sa.Column("job_category", sa.String(length=80), nullable=True))
    op.add_column("listings", sa.Column("employment_type", employment_type_enum, nullable=True))
    op.add_column("listings", sa.Column("workload_min", sa.SmallInteger(), nullable=True))
    op.add_column("listings", sa.Column("workload_max", sa.SmallInteger(), nullable=True))


def downgrade() -> None:
    op.drop_column("listings", "workload_max")
    op.drop_column("listings", "workload_min")
    op.drop_column("listings", "employment_type")
    op.drop_column("listings", "job_category")
    op.drop_column("listings", "has_parking")
    op.drop_column("listings", "property_type")
    op.drop_column("listings", "rooms")
    employment_type_enum.drop(op.get_bind(), checkfirst=True)
    property_type_enum.drop(op.get_bind(), checkfirst=True)
