"""Seed official job-feed provider rows so live ingest can upsert.

Connectors were already in code; ingest failed with "Provider not found" unless
someone posted the row via the admin API. Legal sources only (Adzuna, France
Travail, SmartRecruiters, Workday CXS, Eightfold). Scrapers stay unseeded.

Revision ID: 019
Revises: 018
Create Date: 2026-09-01
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "019"
down_revision: str | None = "018"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_PROVIDERS: tuple[tuple[str, str, str], ...] = (
    ("Adzuna", "adzuna", "https://www.adzuna.ch"),
    ("Adzuna FR", "adzuna-fr", "https://www.adzuna.fr"),
    ("France Travail", "france-travail", "https://francetravail.io"),
    ("SmartRecruiters", "smartrecruiters", "https://www.smartrecruiters.com"),
    ("Richemont", "richemont", "https://careers.richemont.com"),
    ("Lombard Odier", "lombard-odier", "https://www.lombardodier.com/home/careers.html"),
    ("Logitech", "logitech", "https://logitech.wd5.myworkdayjobs.com/Logitech"),
    ("Procter & Gamble", "procter-gamble", "https://pg.wd5.myworkdayjobs.com/1000"),
    ("Temenos", "temenos", "https://temenos.wd103.myworkdayjobs.com/Temenoscareers"),
    (
        "STMicroelectronics",
        "stmicroelectronics",
        "https://stmicroelectronics.eightfold.ai/careers",
    ),
)


def upgrade() -> None:
    for name, slug, base_url in _PROVIDERS:
        op.execute(
            sa.text(
                "INSERT INTO providers (name, slug, base_url, is_active) "
                "SELECT :name, :slug, :base_url, true "
                "WHERE NOT EXISTS (SELECT 1 FROM providers WHERE slug = :slug)"
            ).bindparams(name=name, slug=slug, base_url=base_url)
        )


def downgrade() -> None:
    op.execute(
        sa.text(
            "DELETE FROM providers WHERE slug IN ("
            "'adzuna', 'adzuna-fr', 'france-travail', 'smartrecruiters', "
            "'richemont', 'lombard-odier', 'logitech', 'procter-gamble', "
            "'temenos', 'stmicroelectronics')"
        )
    )
