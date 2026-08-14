from fastapi import APIRouter, HTTPException
from datetime import date
from pydantic import BaseModel, field_validator
from Backend.src.utils.input_validator import (
    is_empty,
    validate_length,
    is_alpha
)
from Backend.src.utils.numeric_validator import (is_positive)

from Backend.src.services.assignment_service import (
    get_all_assignments,
    get_assignment_by_id,
    get_assignments_by_course,
    create_assignment,
    update_assignment,
    delete_assignment,
    submit_assignment,
    get_assignment_submissions,
    update_submission
)

router = APIRouter(
    prefix="/assignments",
    tags=["Assignments"]
)


class Submission(BaseModel):
    student_id: int
    submission_date: date
    submission_file: str
    status: str = "submitted"
    marks: float | None = None
    feedback: str = ""

    @field_validator("student_id")
    @classmethod
    def validate_student_id(cls, value):
        if not is_positive(value):
            raise ValueError("Student ID must be a positive number")
        return value

    @field_validator("submission_file")
    @classmethod
    def validate_submission_file(cls, value):
        if is_empty(value):
            raise ValueError("Submission file cannot be empty")
        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value):
        if is_empty(value):
            raise ValueError("Status cannot be empty")
        return value

    @field_validator("marks")
    @classmethod
    def validate_marks(cls, value):
        if value is not None and not is_positive(value):
            raise ValueError("Marks must be positive")
        return value

class Assignment(BaseModel):
    assignment_id: int
    course_id: int
    title: str
    description: str
    due_date: date
    max_marks: float
    submissions: list[Submission]

    @field_validator("assignment_id", "course_id")
    @classmethod
    def validate_ids(cls, value):
        if not is_positive(value):
            raise ValueError("ID must be a positive number")
        return value

    @field_validator("title")
    @classmethod
    def validate_title(cls, value):
        if is_empty(value):
            raise ValueError("Title cannot be empty")

        if not validate_length(value, 1, 100):
            raise ValueError("Title must be between 1 and 100 characters")

        return value

    @field_validator("description")
    @classmethod
    def validate_description(cls, value):
        if is_empty(value):
            raise ValueError("Description cannot be empty")

        if not validate_length(value, 1, 500):
            raise ValueError(
                "Description must be between 1 and 500 characters"
            )

        return value

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, value):
        if is_empty(value):
            raise ValueError("Due date cannot be empty")
        return value

    @field_validator("max_marks")
    @classmethod
    def validate_max_marks(cls, value):
        if not is_positive(value):
            raise ValueError("Maximum marks must be positive")
        return value


@router.get("/")
def get_assignments():
    return get_all_assignments()


@router.get("/{assignment_id}")
def get_assignment(assignment_id: int):
    assignment = get_assignment_by_id(assignment_id)

    if not assignment:
        raise HTTPException(
            status_code=404,
            detail="Assignment not found"
        )

    return assignment


@router.get("/course/{course_id}")
def get_course_assignments(course_id: int):
    return get_assignments_by_course(course_id)


@router.post("/")
def add_assignment(assignment: Assignment):
    try:
        return create_assignment(assignment.model_dump())

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.put("/{assignment_id}")
def edit_assignment(
    assignment_id: int,
    assignment: Assignment
):
    if not get_assignment_by_id(assignment_id):
        raise HTTPException(
            status_code=404,
            detail="Assignment not found"
        )

    return update_assignment(
        assignment_id,
        assignment.model_dump()
    )


@router.delete("/{assignment_id}")
def remove_assignment(assignment_id: int):
    if not delete_assignment(assignment_id):
        raise HTTPException(
            status_code=404,
            detail="Assignment not found"
        )

    return {
        "message": "Assignment deleted successfully"
    }

@router.post("/{assignment_id}/submit")
def submit(
    assignment_id: int,
    submission: Submission
):
    try:
        result = submit_assignment(
            assignment_id,
            submission.model_dump()
        )

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="Assignment not found"
            )

        return {
            "message": "Assignment submitted successfully",
            "submission": result
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get("/{assignment_id}/submissions")
def get_submissions(assignment_id: int):
    submissions = get_assignment_submissions(assignment_id)

    if submissions is None:
        raise HTTPException(
            status_code=404,
            detail="Assignment not found"
        )

    return submissions


@router.put("/{assignment_id}/submissions/{student_id}")
def edit_submission(
    assignment_id: int,
    student_id: int,
    submission: Submission
):
    result = update_submission(
        assignment_id,
        student_id,
        submission.model_dump()
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Submission not found"
        )

    return {
        "message": "Submission updated successfully",
        "submission": result
    }