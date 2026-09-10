"""attach quizzes directly to courses

Revision ID: e31a2f6c9b04
Revises: d7e61b2a430f
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e31a2f6c9b04"
down_revision: Union[str, Sequence[str], None] = "d7e61b2a430f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("quizzes", sa.Column("course_id", sa.Integer(), nullable=True))
    op.execute(
        """
        UPDATE quizzes q
        SET course_id = m.course_id
        FROM lessons l
        JOIN modules m ON m.module_id = l.module_id
        WHERE q.lesson_id = l.lesson_id
        """
    )
    op.alter_column("quizzes", "course_id", existing_type=sa.Integer(), nullable=False)
    op.create_foreign_key(
        "fk_quizzes_course_id", "quizzes", "courses",
        ["course_id"], ["course_id"], ondelete="CASCADE",
    )
    op.alter_column("quizzes", "lesson_id", existing_type=sa.Integer(), nullable=True)


def downgrade() -> None:
    op.execute("DELETE FROM quizzes WHERE lesson_id IS NULL")
    op.alter_column("quizzes", "lesson_id", existing_type=sa.Integer(), nullable=False)
    op.drop_constraint("fk_quizzes_course_id", "quizzes", type_="foreignkey")
    op.drop_column("quizzes", "course_id")
