"""add announcement targeting and notification links

Revision ID: c42f8a1d9e01
Revises: 8d7f2c1a4b90
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "c42f8a1d9e01"
down_revision: Union[str, Sequence[str], None] = "8d7f2c1a4b90"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("announcements", "course_id", existing_type=sa.Integer(), nullable=True)
    op.add_column("announcements", sa.Column("audience", sa.String(20), nullable=False, server_default="all"))
    op.execute("UPDATE announcements SET audience = 'students_only' WHERE course_id IS NOT NULL")
    op.add_column("notifications", sa.Column("announcement_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_notifications_announcement_id", "notifications", "announcements",
        ["announcement_id"], ["announcement_id"], ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_notifications_announcement_id", "notifications", type_="foreignkey")
    op.drop_column("notifications", "announcement_id")
    op.drop_column("announcements", "audience")
    op.alter_column("announcements", "course_id", existing_type=sa.Integer(), nullable=False)
