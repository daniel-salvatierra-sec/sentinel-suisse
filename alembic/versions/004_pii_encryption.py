"""Encrypt existing PII and add email_lookup column.

Revision ID: 004
Revises: 003
Create Date: 2026-07-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "004"
down_revision: str | None = "003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("email_lookup", sa.String(length=64), nullable=True))
    op.alter_column(
        "users",
        "email",
        existing_type=sa.String(length=320),
        type_=sa.String(length=512),
        existing_nullable=False,
    )
    op.alter_column(
        "notification_channels",
        "channel_address",
        existing_type=sa.String(length=500),
        type_=sa.String(length=1000),
        existing_nullable=False,
    )

    from sentinel_suisse.security.pii import email_lookup as make_email_lookup
    from sentinel_suisse.security.pii import encrypt_pii

    bind = op.get_bind()
    users = bind.execute(sa.text("SELECT id, email FROM users")).fetchall()
    for row in users:
        plain_email = row.email
        if plain_email.startswith("gAAAA"):
            continue
        bind.execute(
            sa.text("UPDATE users SET email_lookup = :lookup, email = :encrypted WHERE id = :id"),
            {
                "lookup": make_email_lookup(plain_email),
                "encrypted": encrypt_pii(plain_email.lower()),
                "id": row.id,
            },
        )

    channels = bind.execute(
        sa.text("SELECT id, channel_address FROM notification_channels")
    ).fetchall()
    for row in channels:
        address = row.channel_address
        if address.startswith("gAAAA"):
            continue
        bind.execute(
            sa.text("UPDATE notification_channels SET channel_address = :enc WHERE id = :id"),
            {"enc": encrypt_pii(address), "id": row.id},
        )

    op.alter_column("users", "email_lookup", nullable=False)
    op.create_unique_constraint("uq_users_email_lookup", "users", ["email_lookup"])
    op.drop_constraint("users_email_key", "users", type_="unique")


def downgrade() -> None:
    from sentinel_suisse.security.pii import decrypt_pii

    bind = op.get_bind()
    users = bind.execute(sa.text("SELECT id, email FROM users")).fetchall()
    for row in users:
        bind.execute(
            sa.text("UPDATE users SET email = :plain WHERE id = :id"),
            {"plain": decrypt_pii(row.email), "id": row.id},
        )

    channels = bind.execute(
        sa.text("SELECT id, channel_address FROM notification_channels")
    ).fetchall()
    for row in channels:
        bind.execute(
            sa.text("UPDATE notification_channels SET channel_address = :plain WHERE id = :id"),
            {"plain": decrypt_pii(row.channel_address), "id": row.id},
        )

    op.drop_constraint("uq_users_email_lookup", "users", type_="unique")
    op.create_unique_constraint("users_email_key", "users", ["email"])
    op.drop_column("users", "email_lookup")
    op.alter_column(
        "users",
        "email",
        existing_type=sa.String(length=512),
        type_=sa.String(length=320),
        existing_nullable=False,
    )
    op.alter_column(
        "notification_channels",
        "channel_address",
        existing_type=sa.String(length=1000),
        type_=sa.String(length=500),
        existing_nullable=False,
    )
