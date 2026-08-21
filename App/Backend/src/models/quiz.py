from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from Backend.database import Base


class Quiz(Base):
    __tablename__ = "quizzes"

    quiz_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    lesson_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("lessons.lesson_id"),
        nullable=False
    )

    title: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    max_marks: Mapped[float] = mapped_column(
        Numeric(6, 2),
        nullable=False
    )

    passing_marks: Mapped[float] = mapped_column(
        Numeric(6, 2),
        nullable=False
    )

    duration_minutes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    max_attempts: Mapped[int] = mapped_column(
        Integer,
        default=1
    )

    is_published: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    question_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    quiz_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("quizzes.quiz_id"),
        nullable=False
    )

    question_text: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    question_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    marks: Mapped[float] = mapped_column(
        Numeric(6, 2),
        nullable=False
    )


class QuestionOption(Base):
    __tablename__ = "question_options"

    option_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    question_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("quiz_questions.question_id"),
        nullable=False
    )

    option_text: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    is_correct: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    __table_args__ = (
        UniqueConstraint(
            "quiz_id",
            "student_id",
            "attempt_number",
            name="uq_quiz_student_attempt"
        ),
    )

    attempt_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    quiz_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("quizzes.quiz_id"),
        nullable=False
    )

    student_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("students.student_id"),
        nullable=False
    )

    attempt_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    marks: Mapped[float | None] = mapped_column(
        Numeric(6, 2),
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="Not Attempted"
    )

    passed: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True
    )


class StudentAnswer(Base):
    __tablename__ = "student_answers"

    __table_args__ = (
        UniqueConstraint(
            "attempt_id",
            "question_id",
            name="uq_attempt_question"
        ),
    )

    answer_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    attempt_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("quiz_attempts.attempt_id"),
        nullable=False
    )

    question_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("quiz_questions.question_id"),
        nullable=False
    )

    selected_option_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("question_options.option_id"),
        nullable=True
    )

    marks_awarded: Mapped[float | None] = mapped_column(
        Numeric(6, 2),
        nullable=True
    )