from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

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
    submission_date: str
    submission_file: str
    status: str = "submitted"
    marks: float | None = None
    feedback: str = ""


class Assignment(BaseModel):
    assignment_id: int
    course_id: int
    title: str
    description: str
    due_date: str
    max_marks: float
    submissions: list[Submission] 


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