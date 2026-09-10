"""add specific teacher announcement target

Revision ID: d7e61b2a430f
Revises: c42f8a1d9e01
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "d7e61b2a430f"
down_revision: Union[str, Sequence[str], None] = "c42f8a1d9e01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("announcements", sa.Column("target_teacher_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_announcements_target_teacher_id", "announcements", "teachers",
        ["target_teacher_id"], ["teacher_id"], ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_announcements_target_teacher_id", "announcements", type_="foreignkey")
    op.drop_column("announcements", "target_teacher_id")
