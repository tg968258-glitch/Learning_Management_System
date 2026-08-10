from fastapi import APIRouter, HTTPException
from services.enrollment_service import (
    get_all_enrollments,
    create_enrollment
)

router = APIRouter(
    prefix="/enrollments",
    tags=["Enrollments"]
)


@router.get("/")
def get_enrollments():
    return get_all_enrollments()


@router.post("/")
def add_new_enrollment(
    enrollment: dict
):

    student_id = enrollment.get("student_id")
    course_id = enrollment.get("course_id")

    if student_id is None or course_id is None:
        raise HTTPException(
            status_code=400,
            detail="student_id and course_id are required"
        )

    result = create_enrollment(
        student_id,
        course_id
    )

    if not result["success"]:
        raise HTTPException(
            status_code=404,
            detail=result["message"]
        )

    return result