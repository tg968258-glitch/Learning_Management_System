"""Read-only academic reports with role-scoped student visibility."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import String, cast, or_
from sqlalchemy.orm import Session

from Backend.database import get_db
from Backend.src.core.auth_dependency import get_current_user, require_roles
from Backend.src.core.course_access import accessible_course_ids
from Backend.src.models.assignment import Assignment, Submission
from Backend.src.models.course import Course
from Backend.src.models.enrollment import Enrollment
from Backend.src.models.lesson import Lesson
from Backend.src.models.module import Module
from Backend.src.models.progress import LessonProgress
from Backend.src.models.quiz import Quiz, QuizAttempt
from Backend.src.models.student import Student
from Backend.src.models.user import User


router = APIRouter(prefix="/reports", tags=["Student Reports"])


def _percentage(scored: float | None, possible: float) -> float | None:
    if scored is None or not possible:
        return None
    return round((scored / possible) * 100, 2)


def _student_report(db: Session, student: Student, allowed_course_ids: set[int] | None) -> dict:
    enrollments = (
        db.query(Enrollment, Course)
        .join(Course, Course.course_id == Enrollment.course_id)
        .filter(Enrollment.student_id == student.student_id)
        .order_by(Course.course_name)
        .all()
    )
    courses = []
    for enrollment, course in enrollments:
        if allowed_course_ids is not None and course.course_id not in allowed_course_ids:
            continue

        lesson_ids = [
            row[0] for row in db.query(Lesson.lesson_id)
            .join(Module, Module.module_id == Lesson.module_id)
            .filter(Module.course_id == course.course_id)
            .all()
        ]
        progress_rows = (
            db.query(LessonProgress)
            .filter(LessonProgress.student_id == student.student_id, LessonProgress.lesson_id.in_(lesson_ids))
            .all()
            if lesson_ids else []
        )
        progress = round(sum(float(row.progress_percentage) for row in progress_rows) / len(lesson_ids), 2) if lesson_ids else 0.0

        assignments = db.query(Assignment).filter(Assignment.course_id == course.course_id).order_by(Assignment.due_date).all()
        assignment_results = []
        assignment_percentages = []
        for assignment in assignments:
            submission = db.query(Submission).filter(
                Submission.assignment_id == assignment.assignment_id,
                Submission.student_id == student.student_id,
            ).first()
            marks = float(submission.marks) if submission and submission.marks is not None else None
            score = _percentage(marks, float(assignment.max_marks))
            if score is not None:
                assignment_percentages.append(score)
            submission_status = submission.status if submission else (
                "missing" if assignment.due_date and assignment.due_date < datetime.utcnow() else "not_submitted"
            )
            assignment_results.append({
                "assignment_id": assignment.assignment_id,
                "title": assignment.title,
                "due_date": assignment.due_date,
                "max_marks": float(assignment.max_marks),
                "marks": marks,
                "grade_percentage": score,
                "submission_status": submission_status,
                "submitted_at": submission.submission_date if submission else None,
                "feedback": submission.feedback if submission else None,
            })

        quizzes = (
            db.query(Quiz)
            .join(Lesson, Lesson.lesson_id == Quiz.lesson_id)
            .join(Module, Module.module_id == Lesson.module_id)
            .filter(Module.course_id == course.course_id)
            .order_by(Quiz.title)
            .all()
        )
        quiz_results = []
        quiz_percentages = []
        for quiz in quizzes:
            attempts = (
                db.query(QuizAttempt)
                .filter(QuizAttempt.quiz_id == quiz.quiz_id, QuizAttempt.student_id == student.student_id)
                .order_by(QuizAttempt.attempt_number.desc())
                .all()
            )
            latest = attempts[0] if attempts else None
            marks = float(latest.marks) if latest and latest.marks is not None else None
            score = _percentage(marks, float(quiz.max_marks))
            if score is not None:
                quiz_percentages.append(score)
            quiz_results.append({
                "quiz_id": quiz.quiz_id,
                "title": quiz.title,
                "max_marks": float(quiz.max_marks),
                "marks": marks,
                "grade_percentage": score,
                "status": latest.status if latest else "not_attempted",
                "passed": latest.passed if latest else None,
                "submitted_at": latest.submitted_at if latest else None,
                "attempt_count": len(attempts),
            })

        scored = assignment_percentages + quiz_percentages
        courses.append({
            "course_id": course.course_id,
            "course_name": course.course_name,
            "enrollment_status": enrollment.status,
            "enrollment_date": enrollment.enrollment_date,
            "progress_percentage": progress,
            "lessons_completed": sum(1 for row in progress_rows if row.completed),
            "lesson_count": len(lesson_ids),
            "performance_percentage": round(sum(scored) / len(scored), 2) if scored else None,
            "assignments": assignment_results,
            "quizzes": quiz_results,
        })

    return {"student_id": student.student_id, "student_name": student.name, "courses": courses}


@router.get("/students/search")
def search_report_students(
    query: str = Query(..., min_length=1, max_length=100),
    limit: int = Query(10, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    """Return only lightweight student identifiers for the report selector."""
    term = query.strip()
    if not term:
        return []
    matches = (
        db.query(Student.student_id, Student.name)
        .filter(or_(
            Student.name.ilike(f"%{term}%"),
            cast(Student.student_id, String).ilike(f"%{term}%"),
        ))
        .order_by(Student.name)
        .limit(limit)
        .all()
    )
    return [{"student_id": student_id, "student_name": name} for student_id, name in matches]


@router.get("/students/{student_id}")
def get_admin_student_report(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return _student_report(db, student, accessible_course_ids(db, current_user))


@router.get("/")
def list_student_reports(
    student_id: int | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return academic reports without exposing any write or grading operation."""
    if current_user.role not in {"admin", "teacher", "student"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to view reports")

    if current_user.role == "student":
        student = db.query(Student).filter(Student.uid == current_user.uid).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student profile not found")
        if student_id is not None and student_id != student.student_id:
            raise HTTPException(status_code=403, detail="Students can view only their own report")
        return [_student_report(db, student, accessible_course_ids(db, current_user))]

    allowed_courses = accessible_course_ids(db, current_user)
    query = db.query(Student)
    if student_id is not None:
        query = query.filter(Student.student_id == student_id)
    students = query.order_by(Student.name).all()
    reports = [_student_report(db, student, allowed_courses) for student in students]
    if current_user.role == "teacher":
        reports = [report for report in reports if report["courses"]]
    return reports
