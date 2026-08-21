from datetime import datetime

from sqlalchemy.orm import Session

from Backend.src.models.assignment import Assignment, Submission
from Backend.src.models.course import Course
from Backend.src.models.module import Module
from Backend.src.models.student import Student
from Backend.src.utils.logger import logger

# =========================================================
# ASSIGNMENTS
# =========================================================

def get_all_assignments(
    db: Session,
    course_id: int | None = None,
    module_id: int | None = None
) -> list[Assignment]:
    query = db.query(Assignment)
    if course_id:
        query = query.filter(Assignment.course_id == course_id)
    if module_id:
        query = query.filter(Assignment.module_id == module_id)
    return query.all()


def get_assignment_by_id(
    db: Session,
    assignment_id: int
) -> Assignment | None:
    return (
        db.query(Assignment)
        .filter(Assignment.assignment_id == assignment_id)
        .first()
    )


def create_assignment(
    db: Session,
    assignment_data: dict,
    created_by_uid: str
) -> Assignment:
    # Verify course and module
    course = db.query(Course).filter(Course.course_id == assignment_data["course_id"]).first()
    if not course:
        raise ValueError("Course does not exist")

    module = db.query(Module).filter(Module.module_id == assignment_data["module_id"]).first()
    if not module:
        raise ValueError("Module does not exist")

    if module.course_id != course.course_id:
        raise ValueError("Module does not belong to the specified course")

    if assignment_data["passing_marks"] > assignment_data["max_marks"]:
        raise ValueError("Passing marks cannot exceed maximum marks")

    assignment = Assignment(
        course_id=assignment_data["course_id"],
        module_id=assignment_data["module_id"],
        title=assignment_data["title"],
        description=assignment_data.get("description"),
        due_date=assignment_data["due_date"],
        max_marks=assignment_data["max_marks"],
        passing_marks=assignment_data["passing_marks"],
        created_by=created_by_uid,
        created_at=datetime.utcnow()
    )

    try:
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        logger.info(f"Assignment created: {assignment.assignment_id}")
        return assignment
    except Exception:
        db.rollback()
        raise


def update_assignment(
    db: Session,
    assignment_id: int,
    updated_data: dict
) -> Assignment | None:
    assignment = get_assignment_by_id(db, assignment_id)
    if not assignment:
        return None

    for field, value in updated_data.items():
        if value is not None and hasattr(assignment, field):
            setattr(assignment, field, value)

    if assignment.passing_marks > assignment.max_marks:
        raise ValueError("Passing marks cannot exceed maximum marks")

    assignment.updated_at = datetime.utcnow()

    try:
        db.commit()
        db.refresh(assignment)
        logger.info(f"Assignment updated: {assignment_id}")
        return assignment
    except Exception:
        db.rollback()
        raise


def delete_assignment(
    db: Session,
    assignment_id: int
) -> Assignment | None:
    assignment = get_assignment_by_id(db, assignment_id)
    if not assignment:
        return None

    try:
        # Delete submissions first
        db.query(Submission).filter(Submission.assignment_id == assignment_id).delete()
        db.delete(assignment)
        db.commit()
        logger.info(f"Assignment deleted: {assignment_id}")
        return assignment
    except Exception:
        db.rollback()
        raise


# =========================================================
# SUBMISSIONS & GRADING
# =========================================================

def get_assignment_submissions(
    db: Session,
    assignment_id: int
) -> list[Submission]:
    return (
        db.query(Submission)
        .filter(Submission.assignment_id == assignment_id)
        .all()
    )


def get_submission(
    db: Session,
    assignment_id: int,
    student_id: int
) -> Submission | None:
    return (
        db.query(Submission)
        .filter(
            Submission.assignment_id == assignment_id,
            Submission.student_id == student_id
        )
        .first()
    )


def submit_assignment(
    db: Session,
    assignment_id: int,
    student_id: int,
    submission_data: dict
) -> Submission:
    assignment = get_assignment_by_id(db, assignment_id)
    if not assignment:
        raise ValueError("Assignment does not exist")

    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise ValueError("Student does not exist")

    # Check for existing submission
    existing = get_submission(db, assignment_id, student_id)
    now = datetime.utcnow()
    status = "submitted"
    if assignment.due_date and now > assignment.due_date:
        status = "late"

    if existing:
        existing.submission_text = submission_data.get("submission_text")
        existing.submission_file = submission_data.get("submission_file")
        existing.submission_date = now
        existing.status = status
        existing.updated_at = now
        submission = existing
    else:
        submission = Submission(
            assignment_id=assignment_id,
            student_id=student_id,
            submission_date=now,
            submission_text=submission_data.get("submission_text"),
            submission_file=submission_data.get("submission_file"),
            status=status,
            created_at=now
        )
        db.add(submission)

    try:
        db.commit()
        db.refresh(submission)
        logger.info(f"Student {student_id} submitted Assignment {assignment_id}")
        return submission
    except Exception:
        db.rollback()
        raise


def grade_submission(
    db: Session,
    assignment_id: int,
    student_id: int,
    marks: float,
    feedback: str | None,
    teacher_id: int
) -> Submission:
    assignment = get_assignment_by_id(db, assignment_id)
    if not assignment:
        raise ValueError("Assignment does not exist")

    if marks > float(assignment.max_marks):
        raise ValueError(f"Marks ({marks}) cannot exceed max marks ({assignment.max_marks})")

    submission = get_submission(db, assignment_id, student_id)
    if not submission:
        raise ValueError("Submission not found for this student")

    submission.marks = marks
    submission.feedback = feedback
    submission.graded_by = teacher_id
    submission.status = "graded"
    submission.updated_at = datetime.utcnow()

    try:
        db.commit()
        db.refresh(submission)
        logger.info(f"Submission {submission.submission_id} graded: {marks} marks")
        return submission
    except Exception:
        db.rollback()
        raise