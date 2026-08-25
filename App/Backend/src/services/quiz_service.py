from sqlalchemy.orm import Session

from Backend.src.models.quiz import (
    QuestionOption,
    Quiz,
    QuizAttempt,
    QuizQuestion,
)
from Backend.src.repositories.lesson_repository import LessonRepository
from Backend.src.repositories.quiz_repository import QuizRepository
from Backend.src.repositories.student_repository import StudentRepository
from Backend.src.utils.logger import logger

# =========================================================
# QUIZ CRUD
# =========================================================

def get_quizzes_by_lesson(
    db: Session,
    lesson_id: int,
    published_only: bool = False
) -> list[Quiz]:
    return QuizRepository.get_by_lesson(db, lesson_id, published_only)


def get_quiz(db: Session, quiz_id: int) -> Quiz | None:
    return QuizRepository.get_by_id(db, quiz_id)


def create_quiz(db: Session, quiz_data: dict) -> Quiz:
    lesson = LessonRepository.get_by_id(db, quiz_data["lesson_id"])
    if not lesson:
        raise ValueError("Lesson does not exist")

    if quiz_data["passing_marks"] > quiz_data["max_marks"]:
        raise ValueError("Passing marks cannot exceed maximum marks")

    quiz = QuizRepository.create_quiz(db, quiz_data)
    logger.info(f"Quiz created: {quiz.quiz_id} for lesson {quiz.lesson_id}")
    return quiz


def update_quiz(db: Session, quiz_id: int, updated_data: dict) -> Quiz | None:
    quiz = QuizRepository.get_by_id(db, quiz_id)
    if not quiz:
        return None

    new_passing = updated_data.get("passing_marks", quiz.passing_marks)
    new_max = updated_data.get("max_marks", quiz.max_marks)
    if new_passing > new_max:
        raise ValueError("Passing marks cannot exceed maximum marks")

    updated = QuizRepository.update_quiz(db, quiz, updated_data)
    logger.info(f"Quiz updated: {quiz_id}")
    return updated


def delete_quiz(db: Session, quiz_id: int) -> Quiz | None:
    quiz = QuizRepository.get_by_id(db, quiz_id)
    if not quiz:
        return None

    QuizRepository.delete_quiz(db, quiz)
    logger.info(f"Quiz deleted: {quiz_id}")
    return quiz


# =========================================================
# QUESTION & OPTIONS
# =========================================================

def add_question_to_quiz(db: Session, quiz_id: int, question_data: dict) -> QuizQuestion:
    quiz = QuizRepository.get_by_id(db, quiz_id)
    if not quiz:
        raise ValueError("Quiz does not exist")

    options_data = question_data.pop("options", [])
    if not options_data:
        raise ValueError("A question must have at least one option")

    return QuizRepository.create_question_with_options(db, quiz_id, question_data, options_data)


def get_quiz_questions(db: Session, quiz_id: int) -> list[QuizQuestion]:
    return QuizRepository.get_questions_by_quiz(db, quiz_id)


def get_question_options(db: Session, question_id: int) -> list[QuestionOption]:
    return QuizRepository.get_options_by_question(db, question_id)


# =========================================================
# QUIZ ATTEMPTS & AUTO-GRADING ENGINE
# =========================================================

def start_quiz_attempt(db: Session, quiz_id: int, student_id: int) -> QuizAttempt:
    quiz = QuizRepository.get_by_id(db, quiz_id)
    if not quiz:
        raise ValueError("Quiz does not exist")
    if not quiz.is_published:
        raise ValueError("Quiz is not published yet")

    student = StudentRepository.get_by_id(db, student_id)
    if not student:
        raise ValueError("Student does not exist")

    existing_attempts = QuizRepository.count_student_attempts(db, quiz_id, student_id)
    if existing_attempts >= quiz.max_attempts:
        raise ValueError(f"Maximum attempt limit ({quiz.max_attempts}) reached for this quiz")

    attempt_number = existing_attempts + 1
    attempt = QuizRepository.create_attempt(db, quiz_id, student_id, attempt_number)
    logger.info(f"Student {student_id} started Quiz {quiz_id} Attempt #{attempt_number}")
    return attempt


def submit_quiz_attempt(
    db: Session,
    attempt_id: int,
    student_id: int,
    answers_data: list[dict]
) -> QuizAttempt:
    attempt = QuizRepository.get_attempt_by_id(db, attempt_id)
    if not attempt:
        raise ValueError("Quiz attempt not found")
    if attempt.student_id != student_id:
        raise ValueError("You can only submit your own quiz attempt")
    if attempt.status != "in_progress":
        raise ValueError("This quiz attempt has already been submitted")

    quiz = QuizRepository.get_by_id(db, attempt.quiz_id)
    if not quiz:
        raise ValueError("Quiz not found")

    total_marks_awarded = 0.0
    evaluated_answers = []

    for ans_item in answers_data:
        question_id = ans_item["question_id"]
        selected_option_id = ans_item.get("selected_option_id")

        question = QuizRepository.get_question_by_id(db, question_id)
        if not question:
            continue

        marks_for_this_q = 0.0
        if selected_option_id:
            option = QuizRepository.get_option_by_id(db, selected_option_id, question_id)
            if option and option.is_correct:
                marks_for_this_q = float(question.marks)

        total_marks_awarded += marks_for_this_q
        evaluated_answers.append({
            "question_id": question_id,
            "selected_option_id": selected_option_id,
            "marks_awarded": marks_for_this_q
        })

    passed = total_marks_awarded >= float(quiz.passing_marks)
    total_score = round(total_marks_awarded, 2)

    completed_attempt = QuizRepository.save_attempt_results(
        db=db,
        attempt=attempt,
        answers=evaluated_answers,
        total_marks=total_score,
        passed=passed
    )
    logger.info(
        f"Quiz Attempt {attempt_id} evaluated: Score {total_score}/{quiz.max_marks} (Passed: {passed})"
    )
    return completed_attempt


def get_student_quiz_attempts(
    db: Session,
    quiz_id: int,
    student_id: int
) -> list[QuizAttempt]:
    return QuizRepository.get_student_attempts(db, quiz_id, student_id)
