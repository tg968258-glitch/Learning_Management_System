from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from Backend.database import get_db
from Backend.src.core.auth_dependency import get_current_user, require_roles
from Backend.src.models.quiz import Quiz, StudentAnswer
from Backend.src.models.student import Student
from Backend.src.models.user import User
from Backend.src.schemas.quizzes import (
    QuestionCreate,
    QuestionResponse,
    QuizAttemptResponse,
    QuizCreate,
    QuizDetailResponse,
    QuizResponse,
    QuizSubmitRequest,
    QuizUpdate,
)
from Backend.src.services.quiz_service import (
    add_question_to_quiz,
    create_quiz,
    delete_quiz,
    get_question_options,
    get_quiz,
    get_quiz_questions,
    get_quizzes_by_lesson,
    get_student_quiz_attempts,
    start_quiz_attempt,
    submit_quiz_attempt,
    update_quiz,
)

router = APIRouter(
    prefix="/quizzes",
    tags=["Quizzes"]
)


def _build_quiz_detail_response(db: Session, quiz: Quiz, is_student: bool = False) -> dict:
    questions = get_quiz_questions(db, quiz.quiz_id)
    questions_list = []
    for q in questions:
        options = get_question_options(db, q.question_id)
        options_list = [
            {
                "option_id": opt.option_id,
                "question_id": opt.question_id,
                "option_text": opt.option_text,
                "is_correct": None if is_student else opt.is_correct
            }
            for opt in options
        ]
        questions_list.append({
            "question_id": q.question_id,
            "quiz_id": q.quiz_id,
            "question_text": q.question_text,
            "question_type": q.question_type,
            "marks": float(q.marks),
            "options": options_list
        })

    return {
        "quiz_id": quiz.quiz_id,
        "lesson_id": quiz.lesson_id,
        "title": quiz.title,
        "description": quiz.description,
        "max_marks": float(quiz.max_marks),
        "passing_marks": float(quiz.passing_marks),
        "duration_minutes": quiz.duration_minutes,
        "max_attempts": quiz.max_attempts,
        "is_published": quiz.is_published,
        "created_at": quiz.created_at,
        "updated_at": quiz.updated_at,
        "questions": questions_list
    }


# =========================================================
# LIST QUIZZES FOR A LESSON
# =========================================================

@router.get("/lesson/{lesson_id}", response_model=list[QuizResponse])
def list_lesson_quizzes(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if lesson_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lesson ID must be positive"
        )

    published_only = current_user.role == "student"
    quizzes = get_quizzes_by_lesson(db, lesson_id, published_only=published_only)
    return [
        {
            "quiz_id": q.quiz_id,
            "lesson_id": q.lesson_id,
            "title": q.title,
            "description": q.description,
            "max_marks": float(q.max_marks),
            "passing_marks": float(q.passing_marks),
            "duration_minutes": q.duration_minutes,
            "max_attempts": q.max_attempts,
            "is_published": q.is_published,
            "created_at": q.created_at,
            "updated_at": q.updated_at
        }
        for q in quizzes
    ]


# =========================================================
# GET SINGLE QUIZ WITH QUESTIONS
# =========================================================

@router.get("/{quiz_id}", response_model=QuizDetailResponse)
def get_single_quiz(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if quiz_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quiz ID must be positive"
        )

    quiz = get_quiz(db, quiz_id)
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )

    if current_user.role == "student" and not quiz.is_published:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Quiz is not published yet"
        )

    return _build_quiz_detail_response(db, quiz, is_student=(current_user.role == "student"))


# =========================================================
# CREATE QUIZ (Admin or Teacher)
# =========================================================

@router.post("/", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
def add_new_quiz(
    quiz_in: QuizCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher"))
):
    try:
        created = create_quiz(db, quiz_in.model_dump())
        return {
            "quiz_id": created.quiz_id,
            "lesson_id": created.lesson_id,
            "title": created.title,
            "description": created.description,
            "max_marks": float(created.max_marks),
            "passing_marks": float(created.passing_marks),
            "duration_minutes": created.duration_minutes,
            "max_attempts": created.max_attempts,
            "is_published": created.is_published,
            "created_at": created.created_at,
            "updated_at": created.updated_at
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e


# =========================================================
# ADD QUESTION TO QUIZ (Admin or Teacher)
# =========================================================

@router.post("/{quiz_id}/questions", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
def add_question(
    quiz_id: int,
    question_in: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher"))
):
    try:
        created_q = add_question_to_quiz(db, quiz_id, question_in.model_dump())
        options = get_question_options(db, created_q.question_id)
        return {
            "question_id": created_q.question_id,
            "quiz_id": created_q.quiz_id,
            "question_text": created_q.question_text,
            "question_type": created_q.question_type,
            "marks": float(created_q.marks),
            "options": [
                {
                    "option_id": opt.option_id,
                    "question_id": opt.question_id,
                    "option_text": opt.option_text,
                    "is_correct": opt.is_correct
                }
                for opt in options
            ]
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e


# =========================================================
# UPDATE QUIZ (Admin or Teacher)
# =========================================================

@router.put("/{quiz_id}", response_model=QuizResponse)
def update_existing_quiz(
    quiz_id: int,
    quiz_in: QuizUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher"))
):
    if quiz_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quiz ID must be positive"
        )

    try:
        updated = update_quiz(db, quiz_id, quiz_in.model_dump(exclude_unset=True))
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found"
            )

        return {
            "quiz_id": updated.quiz_id,
            "lesson_id": updated.lesson_id,
            "title": updated.title,
            "description": updated.description,
            "max_marks": float(updated.max_marks),
            "passing_marks": float(updated.passing_marks),
            "duration_minutes": updated.duration_minutes,
            "max_attempts": updated.max_attempts,
            "is_published": updated.is_published,
            "created_at": updated.created_at,
            "updated_at": updated.updated_at
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e


# =========================================================
# DELETE QUIZ (Admin or Teacher)
# =========================================================

@router.delete("/{quiz_id}")
def remove_quiz(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher"))
):
    if quiz_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quiz ID must be positive"
        )

    deleted = delete_quiz(db, quiz_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )

    return {"message": "Quiz deleted successfully"}


# =========================================================
# START QUIZ ATTEMPT (Student only)
# =========================================================

@router.post("/{quiz_id}/start", response_model=QuizAttemptResponse, status_code=status.HTTP_201_CREATED)
def start_attempt(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("student"))
):
    student = db.query(Student).filter(Student.uid == current_user.uid).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )

    try:
        attempt = start_quiz_attempt(db, quiz_id, student.student_id)
        return {
            "attempt_id": attempt.attempt_id,
            "quiz_id": attempt.quiz_id,
            "student_id": attempt.student_id,
            "attempt_number": attempt.attempt_number,
            "started_at": attempt.started_at,
            "submitted_at": attempt.submitted_at,
            "marks": float(attempt.marks) if attempt.marks is not None else None,
            "status": attempt.status,
            "passed": attempt.passed,
            "answers": []
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e


# =========================================================
# SUBMIT QUIZ ATTEMPT (Student only - Evaluates automatically)
# =========================================================

@router.post("/attempts/{attempt_id}/submit", response_model=QuizAttemptResponse)
def submit_attempt(
    attempt_id: int,
    submit_req: QuizSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("student"))
):
    student = db.query(Student).filter(Student.uid == current_user.uid).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )

    try:
        attempt = submit_quiz_attempt(
            db=db,
            attempt_id=attempt_id,
            student_id=student.student_id,
            answers_data=[a.model_dump() for a in submit_req.answers]
        )
        answers = (
            db.query(StudentAnswer)
            .filter(StudentAnswer.attempt_id == attempt.attempt_id)
            .all()
        )
        return {
            "attempt_id": attempt.attempt_id,
            "quiz_id": attempt.quiz_id,
            "student_id": attempt.student_id,
            "attempt_number": attempt.attempt_number,
            "started_at": attempt.started_at,
            "submitted_at": attempt.submitted_at,
            "marks": float(attempt.marks) if attempt.marks is not None else None,
            "status": attempt.status,
            "passed": attempt.passed,
            "answers": [
                {
                    "answer_id": ans.answer_id,
                    "attempt_id": ans.attempt_id,
                    "question_id": ans.question_id,
                    "selected_option_id": ans.selected_option_id,
                    "marks_awarded": float(ans.marks_awarded) if ans.marks_awarded is not None else None
                }
                for ans in answers
            ]
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e


# =========================================================
# GET MY ATTEMPTS (Student)
# =========================================================

@router.get("/{quiz_id}/my-attempts", response_model=list[QuizAttemptResponse])
def get_my_attempts(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("student"))
):
    student = db.query(Student).filter(Student.uid == current_user.uid).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )

    attempts = get_student_quiz_attempts(db, quiz_id, student.student_id)
    result = []
    for att in attempts:
        answers = (
            db.query(StudentAnswer)
            .filter(StudentAnswer.attempt_id == att.attempt_id)
            .all()
        )
        result.append({
            "attempt_id": att.attempt_id,
            "quiz_id": att.quiz_id,
            "student_id": att.student_id,
            "attempt_number": att.attempt_number,
            "started_at": att.started_at,
            "submitted_at": att.submitted_at,
            "marks": float(att.marks) if att.marks is not None else None,
            "status": att.status,
            "passed": att.passed,
            "answers": [
                {
                    "answer_id": ans.answer_id,
                    "attempt_id": ans.attempt_id,
                    "question_id": ans.question_id,
                    "selected_option_id": ans.selected_option_id,
                    "marks_awarded": float(ans.marks_awarded) if ans.marks_awarded is not None else None
                }
                for ans in answers
            ]
        })
    return result
