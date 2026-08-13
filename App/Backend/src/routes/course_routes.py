from fastapi import APIRouter, HTTPException, Body

from Backend.src.services.course_service import (
    get_all_courses,
    get_course,
    create_course,
    update_course,
    delete_course,
    get_course_syllabus,
    update_course_syllabus
)


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
def add_course(course: dict):

    return create_course(course)


@router.put("/{course_id}")
def edit_course(
    course_id: int,
    course: dict
):

    updated_course = update_course(
        course_id,
        course
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