"""Add DE/IT to country_code for German and Italian border jobs.

Revision ID: 014
Revises: 013
Create Date: 2026-08-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "014"
down_revision: str | None = "013"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute(sa.text("ALTER TYPE country_code ADD VALUE IF NOT EXISTS 'DE'"))
        op.execute(sa.text("ALTER TYPE country_code ADD VALUE IF NOT EXISTS 'IT'"))
    op.execute(
        sa.text(
            "INSERT INTO providers (name, slug, base_url, is_active) "
            "SELECT 'Adzuna DE', 'adzuna-de', 'https://www.adzuna.de', true "
            "WHERE NOT EXISTS (SELECT 1 FROM providers WHERE slug = 'adzuna-de')"
        )
    )
    op.execute(
        sa.text(
            "INSERT INTO providers (name, slug, base_url, is_active) "
            "SELECT 'Adzuna IT', 'adzuna-it', 'https://www.adzuna.it', true "
            "WHERE NOT EXISTS (SELECT 1 FROM providers WHERE slug = 'adzuna-it')"
        )
    )


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM providers WHERE slug IN ('adzuna-de', 'adzuna-it')"))
