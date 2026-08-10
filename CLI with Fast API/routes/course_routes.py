from fastapi import APIRouter, HTTPException
from services.course_service import (
    get_all_courses,
    get_course,
    create_course,
    update_course_data,
    remove_course
)

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.get("/")
def get_courses():
    return get_all_courses()


@router.get("/{course_id}")
def get_single_course(course_id: int):

    course = get_course(course_id)

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    return course


@router.post("/")
def add_new_course(course: dict):

    result = create_course(course)

    return {
        "message": "Course added successfully",
        "course": result
    }


@router.put("/{course_id}")
def update_existing_course(
    course_id: int,
    course_data: dict
):

    result = update_course_data(
        course_id,
        course_data
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    return {
        "message": "Course updated successfully",
        "course": result
    }


@router.delete("/{course_id}")
def delete_existing_course(course_id: int):

    result = remove_course(course_id)

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    return {
        "message": "Course deleted successfully"
    }