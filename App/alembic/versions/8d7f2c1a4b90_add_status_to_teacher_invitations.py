"""add status to teacher invitations

Revision ID: 8d7f2c1a4b90
Revises: 5b1ff5e5abae
Create Date: 2026-09-08

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8d7f2c1a4b90"
down_revision: Union[str, Sequence[str], None] = "5b1ff5e5abae"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # The server default safely backfills all existing rows as Pending and
    # also protects inserts performed outside the ORM.
    op.add_column(
        "teacher_invitations",
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default=sa.text("'Pending'"),
        ),
    )


def downgrade() -> None:
    op.drop_column("teacher_invitations", "status")
