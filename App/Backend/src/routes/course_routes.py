from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, field_validator

from Backend.src.utils.input_validator import (
    is_empty,
    validate_length,
    is_alpha
)

from Backend.src.services.course_service import (
    get_all_courses,
    get_course,
    create_course,
    update_course,
    delete_course,
    get_course_syllabus,
    update_course_syllabus
)

class Course(BaseModel):
    course_name: str
    duration: str

    @field_validator("course_name")
    @classmethod
    def validate_course_name(cls, value):
        if is_empty(value):
            raise ValueError("Course name cannot be empty")

        if not is_alpha(value):
            raise ValueError(
                "Course name must contain only alphabets and spaces"
            )

        if not validate_length(value, 2, 100):
            raise ValueError(
                "Course name must be between 2 and 100 characters"
            )

        return value

    @field_validator("duration")
    @classmethod
    def validate_duration(cls, value):
        if is_empty(value):
            raise ValueError("Duration cannot be empty")

        if not validate_length(value, 1, 50):
            raise ValueError(
                "Duration must be between 1 and 50 characters"
            )

        return value


class CourseUpdate(Course):
    course_name: str | None = None
    duration: str | None = None


router = APIRouter(
    prefix="/courses",
    tags=["Courses"]
)


# =========================
# COURSE CRUD
# =========================

@router.get("/")
def get_courses():

    return get_all_courses()


@router.get("/{course_id}")
def get_course_by_id(course_id: int):

    course = get_course(course_id)

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    return course


@router.post("/")
def add_course(course: Course):
    return create_course(course.model_dump())


@router.put("/{course_id}")
def edit_course(
    course_id: int,
    course: CourseUpdate
):

    updated_course = update_course(
        course_id,
        course.model_dump(exclude_unset=True)
    )

    if not updated_course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    return updated_course


@router.delete("/{course_id}")
def remove_course(course_id: int):

    deleted_course = delete_course(
        course_id
    )

    if not deleted_course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    return {
        "message": "Course deleted successfully"
    }


# =========================
# SYLLABUS
# =========================

@router.get("/{course_id}/syllabus")
def get_syllabus(course_id: int):

    syllabus = get_course_syllabus(
        course_id
    )

    if syllabus is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    return {
        "course_id": course_id,
        "syllabus": syllabus
    }


@router.put("/{course_id}/syllabus")
def update_syllabus(
    course_id: int,
    syllabus: list = Body(...)
):

    updated_course = update_course_syllabus(
        course_id,
        syllabus
    )

    if not updated_course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    return {
        "message": "Syllabus updated successfully",
        "course_id": course_id,
        "syllabus": updated_course["syllabus"]
    }