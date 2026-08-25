from datetime import datetime
from sqlalchemy.orm import Session

from Backend.src.models.assignment import Assignment, Submission
from Backend.src.repositories.assignment_repository import AssignmentRepository
from Backend.src.repositories.course_repository import CourseRepository
from Backend.src.repositories.module_repository import ModuleRepository
from Backend.src.repositories.student_repository import StudentRepository
from Backend.src.utils.logger import logger

# =========================================================
# ASSIGNMENTS
# =========================================================

def get_all_assignments(
    db: Session,
    course_id: int | None = None,
    module_id: int | None = None
) -> list[Assignment]:
    return AssignmentRepository.get_all(db, course_id=course_id, module_id=module_id)


def get_assignment_by_id(
    db: Session,
    assignment_id: int
) -> Assignment | None:
    return AssignmentRepository.get_by_id(db, assignment_id)


def create_assignment(
    db: Session,
    assignment_data: dict,
    created_by_uid: str
) -> Assignment:
    # Business validations
    course = CourseRepository.get_by_id(db, assignment_data["course_id"])
    if not course:
        raise ValueError("Course does not exist")

    module = ModuleRepository.get_by_id(db, assignment_data["module_id"])
    if not module:
        raise ValueError("Module does not exist")

    if module.course_id != course.course_id:
        raise ValueError("Module does not belong to the specified course")

    if assignment_data["passing_marks"] > assignment_data["max_marks"]:
        raise ValueError("Passing marks cannot exceed maximum marks")

    assignment = AssignmentRepository.create(db, assignment_data, created_by_uid)
    logger.info(f"Assignment created: {assignment.assignment_id}")
    return assignment


def update_assignment(
    db: Session,
    assignment_id: int,
    updated_data: dict
) -> Assignment | None:
    assignment = AssignmentRepository.get_by_id(db, assignment_id)
    if not assignment:
        return None

    new_passing = updated_data.get("passing_marks", assignment.passing_marks)
    new_max = updated_data.get("max_marks", assignment.max_marks)
    if new_passing > new_max:
        raise ValueError("Passing marks cannot exceed maximum marks")

    updated = AssignmentRepository.update(db, assignment, updated_data)
    logger.info(f"Assignment updated: {assignment_id}")
    return updated


def delete_assignment(
    db: Session,
    assignment_id: int
) -> Assignment | None:
    assignment = AssignmentRepository.get_by_id(db, assignment_id)
    if not assignment:
        return None

    AssignmentRepository.delete(db, assignment)
    logger.info(f"Assignment deleted: {assignment_id}")
    return assignment


# =========================================================
# SUBMISSIONS & GRADING
# =========================================================

def get_assignment_submissions(
    db: Session,
    assignment_id: int
) -> list[Submission]:
    return AssignmentRepository.get_submissions_by_assignment(db, assignment_id)


def get_submission(
    db: Session,
    assignment_id: int,
    student_id: int
) -> Submission | None:
    return AssignmentRepository.get_submission(db, assignment_id, student_id)


def submit_assignment(
    db: Session,
    assignment_id: int,
    student_id: int,
    submission_data: dict
) -> Submission:
    assignment = AssignmentRepository.get_by_id(db, assignment_id)
    if not assignment:
        raise ValueError("Assignment does not exist")

    student = StudentRepository.get_by_id(db, student_id)
    if not student:
        raise ValueError("Student does not exist")

    submission_text = submission_data.get("submission_text")
    submission_file = submission_data.get("submission_file")

    if not submission_text and not submission_file:
        raise ValueError("Submission must include text or an uploaded file")

    now = datetime.utcnow()
    status = "submitted"
    if assignment.due_date and now > assignment.due_date:
        status = "late"

    submission = AssignmentRepository.create_or_update_submission(
        db=db,
        assignment_id=assignment_id,
        student_id=student_id,
        submission_text=submission_text,
        submission_file=submission_file,
        status=status
    )
    logger.info(f"Student {student_id} submitted Assignment {assignment_id}")
    return submission


def grade_submission(
    db: Session,
    assignment_id: int,
    student_id: int,
    marks: float,
    feedback: str | None,
    teacher_id: int | None
) -> Submission:
    assignment = AssignmentRepository.get_by_id(db, assignment_id)
    if not assignment:
        raise ValueError("Assignment does not exist")

    if marks > float(assignment.max_marks):
        raise ValueError(f"Marks ({marks}) cannot exceed max marks ({assignment.max_marks})")

    submission = AssignmentRepository.get_submission(db, assignment_id, student_id)
    if not submission:
        raise ValueError("Submission not found for this student")

    graded = AssignmentRepository.grade_submission(
        db=db,
        submission=submission,
        marks=marks,
        feedback=feedback,
        teacher_id=teacher_id
    )
    logger.info(f"Submission {graded.submission_id} graded: {marks} marks")
    return graded