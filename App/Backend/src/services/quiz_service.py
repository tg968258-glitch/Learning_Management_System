from datetime import datetime

from sqlalchemy.orm import Session

from Backend.src.models.lesson import Lesson
from Backend.src.models.quiz import (
    QuestionOption,
    Quiz,
    QuizAttempt,
    QuizQuestion,
    StudentAnswer,
)
from Backend.src.models.student import Student
from Backend.src.utils.logger import logger

# =========================================================
# QUIZ CRUD
# =========================================================

def get_quizzes_by_lesson(
    db: Session,
    lesson_id: int,
    published_only: bool = False
) -> list[Quiz]:
    query = db.query(Quiz).filter(Quiz.lesson_id == lesson_id)
    if published_only:
        query = query.filter(Quiz.is_published.is_(True))
    return query.all()


def get_quiz(db: Session, quiz_id: int) -> Quiz | None:
    return db.query(Quiz).filter(Quiz.quiz_id == quiz_id).first()


def create_quiz(db: Session, quiz_data: dict) -> Quiz:
    lesson = db.query(Lesson).filter(Lesson.lesson_id == quiz_data["lesson_id"]).first()
    if not lesson:
        raise ValueError("Lesson does not exist")

    if quiz_data["passing_marks"] > quiz_data["max_marks"]:
        raise ValueError("Passing marks cannot exceed maximum marks")

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

    try:
        db.add(quiz)
        db.commit()
        db.refresh(quiz)
        logger.info(f"Quiz created: {quiz.quiz_id} for lesson {quiz.lesson_id}")
        return quiz
    except Exception:
        db.rollback()
        raise


def update_quiz(db: Session, quiz_id: int, updated_data: dict) -> Quiz | None:
    quiz = get_quiz(db, quiz_id)
    if not quiz:
        return None

    for field, value in updated_data.items():
        if value is not None and hasattr(quiz, field):
            setattr(quiz, field, value)

    if quiz.passing_marks > quiz.max_marks:
        raise ValueError("Passing marks cannot exceed maximum marks")

    quiz.updated_at = datetime.utcnow()

    try:
        db.commit()
        db.refresh(quiz)
        logger.info(f"Quiz updated: {quiz_id}")
        return quiz
    except Exception:
        db.rollback()
        raise


def delete_quiz(db: Session, quiz_id: int) -> Quiz | None:
    quiz = get_quiz(db, quiz_id)
    if not quiz:
        return None

    try:
        # Delete questions, options, attempts
        questions = db.query(QuizQuestion).filter(QuizQuestion.quiz_id == quiz_id).all()
        for q in questions:
            db.query(QuestionOption).filter(QuestionOption.question_id == q.question_id).delete()
        db.query(QuizQuestion).filter(QuizQuestion.quiz_id == quiz_id).delete()

        attempts = db.query(QuizAttempt).filter(QuizAttempt.quiz_id == quiz_id).all()
        for att in attempts:
            db.query(StudentAnswer).filter(StudentAnswer.attempt_id == att.attempt_id).delete()
        db.query(QuizAttempt).filter(QuizAttempt.quiz_id == quiz_id).delete()

        db.delete(quiz)
        db.commit()
        logger.info(f"Quiz deleted: {quiz_id}")
        return quiz
    except Exception:
        db.rollback()
        raise


# =========================================================
# QUESTION & OPTIONS
# =========================================================

def add_question_to_quiz(db: Session, quiz_id: int, question_data: dict) -> QuizQuestion:
    quiz = get_quiz(db, quiz_id)
    if not quiz:
        raise ValueError("Quiz does not exist")

    options_data = question_data.pop("options", [])
    if not options_data:
        raise ValueError("A question must have at least one option")

    question = QuizQuestion(
        quiz_id=quiz_id,
        question_text=question_data["question_text"],
        question_type=question_data.get("question_type", "mcq"),
        marks=question_data.get("marks", 1.0)
    )

    try:
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
    except Exception:
        db.rollback()
        raise


def get_quiz_questions(db: Session, quiz_id: int) -> list[QuizQuestion]:
    return db.query(QuizQuestion).filter(QuizQuestion.quiz_id == quiz_id).all()


def get_question_options(db: Session, question_id: int) -> list[QuestionOption]:
    return db.query(QuestionOption).filter(QuestionOption.question_id == question_id).all()


# =========================================================
# QUIZ ATTEMPTS & AUTO-GRADING ENGINE
# =========================================================

def start_quiz_attempt(db: Session, quiz_id: int, student_id: int) -> QuizAttempt:
    quiz = get_quiz(db, quiz_id)
    if not quiz:
        raise ValueError("Quiz does not exist")
    if not quiz.is_published:
        raise ValueError("Quiz is not published yet")

    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise ValueError("Student does not exist")

    # Check attempt count
    existing_attempts = (
        db.query(QuizAttempt)
        .filter(QuizAttempt.quiz_id == quiz_id, QuizAttempt.student_id == student_id)
        .count()
    )
    if existing_attempts >= quiz.max_attempts:
        raise ValueError(f"Maximum attempt limit ({quiz.max_attempts}) reached for this quiz")

    attempt_number = existing_attempts + 1
    attempt = QuizAttempt(
        quiz_id=quiz_id,
        student_id=student_id,
        attempt_number=attempt_number,
        started_at=datetime.utcnow(),
        status="in_progress",
        marks=0.0,
        passed=False
    )

    try:
        db.add(attempt)
        db.commit()
        db.refresh(attempt)
        logger.info(f"Student {student_id} started Quiz {quiz_id} Attempt #{attempt_number}")
        return attempt
    except Exception:
        db.rollback()
        raise


def submit_quiz_attempt(
    db: Session,
    attempt_id: int,
    student_id: int,
    answers_data: list[dict]
) -> QuizAttempt:
    attempt = db.query(QuizAttempt).filter(QuizAttempt.attempt_id == attempt_id).first()
    if not attempt:
        raise ValueError("Quiz attempt not found")
    if attempt.student_id != student_id:
        raise ValueError("You can only submit your own quiz attempt")
    if attempt.status != "in_progress":
        raise ValueError("This quiz attempt has already been submitted")

    quiz = get_quiz(db, attempt.quiz_id)
    if not quiz:
        raise ValueError("Quiz not found")

    total_marks_awarded = 0.0

    try:
        for ans_item in answers_data:
            question_id = ans_item["question_id"]
            selected_option_id = ans_item.get("selected_option_id")

            question = db.query(QuizQuestion).filter(QuizQuestion.question_id == question_id).first()
            if not question:
                continue

            marks_for_this_q = 0.0
            if selected_option_id:
                option = (
                    db.query(QuestionOption)
                    .filter(
                        QuestionOption.option_id == selected_option_id,
                        QuestionOption.question_id == question_id
                    )
                    .first()
                )
                if option and option.is_correct:
                    marks_for_this_q = float(question.marks)

            total_marks_awarded += marks_for_this_q

            student_answer = StudentAnswer(
                attempt_id=attempt.attempt_id,
                question_id=question_id,
                selected_option_id=selected_option_id,
                marks_awarded=marks_for_this_q
            )
            db.add(student_answer)

        attempt.marks = round(total_marks_awarded, 2)
        attempt.passed = total_marks_awarded >= float(quiz.passing_marks)
        attempt.submitted_at = datetime.utcnow()
        attempt.status = "completed"

        db.commit()
        db.refresh(attempt)
        logger.info(
            f"Quiz Attempt {attempt_id} evaluated: Score {attempt.marks}/{quiz.max_marks} (Passed: {attempt.passed})"
        )
        return attempt

    except Exception:
        db.rollback()
        raise


def get_student_quiz_attempts(
    db: Session,
    quiz_id: int,
    student_id: int
) -> list[QuizAttempt]:
    return (
        db.query(QuizAttempt)
        .filter(QuizAttempt.quiz_id == quiz_id, QuizAttempt.student_id == student_id)
        .order_by(QuizAttempt.attempt_number.asc())
        .all()
    )
