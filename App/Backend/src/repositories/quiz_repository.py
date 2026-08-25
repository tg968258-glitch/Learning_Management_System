from datetime import datetime
from sqlalchemy.orm import Session

from Backend.src.models.quiz import (
    QuestionOption,
    Quiz,
    QuizAttempt,
    QuizQuestion,
    StudentAnswer,
)


class QuizRepository:
    # --- Quiz CRUD ---
    @staticmethod
    def get_by_id(db: Session, quiz_id: int) -> Quiz | None:
        return db.query(Quiz).filter(Quiz.quiz_id == quiz_id).first()

    @staticmethod
    def get_by_lesson(
        db: Session,
        lesson_id: int,
        published_only: bool = False
    ) -> list[Quiz]:
        query = db.query(Quiz).filter(Quiz.lesson_id == lesson_id)
        if published_only:
            query = query.filter(Quiz.is_published.is_(True))
        return query.all()

    @staticmethod
    def create_quiz(db: Session, quiz_data: dict) -> Quiz:
        quiz = Quiz(
            lesson_id=quiz_data["lesson_id"],
            title=quiz_data["title"],
            description=quiz_data.get("description"),
            max_marks=quiz_data["max_marks"],
            passing_marks=quiz_data["passing_marks"],
            duration_minutes=quiz_data.get("duration_minutes"),
            max_attempts=quiz_data.get("max_attempts", 1),
            is_published=quiz_data.get("is_published", False),
            created_at=datetime.utcnow()
        )
        db.add(quiz)
        db.commit()
        db.refresh(quiz)
        return quiz

    @staticmethod
    def update_quiz(db: Session, quiz: Quiz, update_data: dict) -> Quiz:
        for field, value in update_data.items():
            if hasattr(quiz, field) and value is not None:
                setattr(quiz, field, value)
        quiz.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(quiz)
        return quiz

    @staticmethod
    def delete_quiz(db: Session, quiz: Quiz) -> None:
        questions = db.query(QuizQuestion).filter(QuizQuestion.quiz_id == quiz.quiz_id).all()
        for q in questions:
            db.query(QuestionOption).filter(QuestionOption.question_id == q.question_id).delete()
        db.query(QuizQuestion).filter(QuizQuestion.quiz_id == quiz.quiz_id).delete()

        attempts = db.query(QuizAttempt).filter(QuizAttempt.quiz_id == quiz.quiz_id).all()
        for att in attempts:
            db.query(StudentAnswer).filter(StudentAnswer.attempt_id == att.attempt_id).delete()
        db.query(QuizAttempt).filter(QuizAttempt.quiz_id == quiz.quiz_id).delete()

        db.delete(quiz)
        db.commit()

    # --- Questions & Options ---
    @staticmethod
    def get_questions_by_quiz(db: Session, quiz_id: int) -> list[QuizQuestion]:
        return db.query(QuizQuestion).filter(QuizQuestion.quiz_id == quiz_id).all()

    @staticmethod
    def get_question_by_id(db: Session, question_id: int) -> QuizQuestion | None:
        return db.query(QuizQuestion).filter(QuizQuestion.question_id == question_id).first()

    @staticmethod
    def create_question_with_options(
        db: Session,
        quiz_id: int,
        question_data: dict,
        options_data: list[dict]
    ) -> QuizQuestion:
        question = QuizQuestion(
            quiz_id=quiz_id,
            question_text=question_data["question_text"],
            question_type=question_data.get("question_type", "mcq"),
            marks=question_data.get("marks", 1.0)
        )
        db.add(question)
        db.flush()

        for opt in options_data:
            option = QuestionOption(
                question_id=question.question_id,
                option_text=opt["option_text"],
                is_correct=opt.get("is_correct", False)
            )
            db.add(option)

        db.commit()
        db.refresh(question)
        return question

    @staticmethod
    def get_options_by_question(db: Session, question_id: int) -> list[QuestionOption]:
        return db.query(QuestionOption).filter(QuestionOption.question_id == question_id).all()

    @staticmethod
    def get_option_by_id(db: Session, option_id: int, question_id: int) -> QuestionOption | None:
        return (
            db.query(QuestionOption)
            .filter(
                QuestionOption.option_id == option_id,
                QuestionOption.question_id == question_id
            )
            .first()
        )

    # --- Attempts ---
    @staticmethod
    def count_student_attempts(db: Session, quiz_id: int, student_id: int) -> int:
        return (
            db.query(QuizAttempt)
            .filter(QuizAttempt.quiz_id == quiz_id, QuizAttempt.student_id == student_id)
            .count()
        )

    @staticmethod
    def get_attempt_by_id(db: Session, attempt_id: int) -> QuizAttempt | None:
        return db.query(QuizAttempt).filter(QuizAttempt.attempt_id == attempt_id).first()

    @staticmethod
    def create_attempt(
        db: Session,
        quiz_id: int,
        student_id: int,
        attempt_number: int
    ) -> QuizAttempt:
        attempt = QuizAttempt(
            quiz_id=quiz_id,
            student_id=student_id,
            attempt_number=attempt_number,
            started_at=datetime.utcnow(),
            status="in_progress",
            marks=0.0,
            passed=False
        )
        db.add(attempt)
        db.commit()
        db.refresh(attempt)
        return attempt

    @staticmethod
    def save_attempt_results(
        db: Session,
        attempt: QuizAttempt,
        answers: list[dict],
        total_marks: float,
        passed: bool
    ) -> QuizAttempt:
        for ans in answers:
            student_ans = StudentAnswer(
                attempt_id=attempt.attempt_id,
                question_id=ans["question_id"],
                selected_option_id=ans.get("selected_option_id"),
                marks_awarded=ans.get("marks_awarded", 0.0)
            )
            db.add(student_ans)

        attempt.marks = total_marks
        attempt.passed = passed
        attempt.submitted_at = datetime.utcnow()
        attempt.status = "completed"

        db.commit()
        db.refresh(attempt)
        return attempt

    @staticmethod
    def get_student_attempts(db: Session, quiz_id: int, student_id: int) -> list[QuizAttempt]:
        return (
            db.query(QuizAttempt)
            .filter(QuizAttempt.quiz_id == quiz_id, QuizAttempt.student_id == student_id)
            .order_by(QuizAttempt.attempt_number.asc())
            .all()
        )
