from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from Backend.database import get_db
from Backend.src.core.auth_dependency import get_current_user, require_roles
from Backend.src.models.user import User
from Backend.src.schemas.courses import (
    CourseAssignTeachers,
    CourseCreate,
    CourseResponse,
    CourseUpdate,
)
from Backend.src.services.course_service import (
    assign_teachers_to_course,
    create_course,
    delete_course,
    get_all_courses,
    get_course,
    get_course_teachers,
    get_teacher_courses,
    publish_course,
    update_course,
)

router = APIRouter(
    prefix="/courses",
    tags=["Courses"]
)


def _build_course_response(db: Session, course) -> dict:
    teachers = get_course_teachers(db, course.course_id)
    return {
        "course_id": course.course_id,
        "course_name": course.course_name,
        "description": course.description,
        "duration": course.duration,
        "status": course.status,
        "category": course.category,
        "created_by": course.created_by,
        "published_by": course.published_by,
        "created_at": course.created_at,
        "updated_at": course.updated_at,
        "teachers": [
            {
                "teacher_id": t.teacher_id,
                "name": t.name,
                "specialization": t.specialization,
            }
            for t in teachers
        ],
    }


# =========================================================
# LIST COURSES
# =========================================================

@router.get("/", response_model=list[CourseResponse])
def list_courses(
    status: str | None = Query(None, description="Filter by status (e.g. active, draft)"),
    category: str | None = Query(None, description="Filter by category"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    courses = get_all_courses(db, status=status, category=category)
    return [_build_course_response(db, c) for c in courses]


# =========================================================
# GET SINGLE COURSE
# =========================================================

@router.get("/{course_id}", response_model=CourseResponse)
def get_course_by_id(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if course_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course ID must be positive"
        )

    course = get_course(db, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    return _build_course_response(db, course)


# =========================================================
# CREATE COURSE (Admin or Teacher)
# =========================================================

@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def add_new_course(
    course_in: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher"))
):
    try:
        created = create_course(
            db=db,
            course_data=course_in.model_dump(),
            created_by_uid=current_user.uid
        )
        return _build_course_response(db, created)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e


# =========================================================
# UPDATE COURSE (Admin or Teacher)
# =========================================================

@router.put("/{course_id}", response_model=CourseResponse)
def update_existing_course(
    course_id: int,
    course_in: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher"))
):
    if course_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course ID must be positive"
        )

    updated = update_course(
        db=db,
        course_id=course_id,
        updated_data=course_in.model_dump(exclude_unset=True)
    )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    return _build_course_response(db, updated)


# =========================================================
# DELETE COURSE (Admin only)
# =========================================================

@router.delete("/{course_id}")
def remove_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    if course_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course ID must be positive"
        )

    deleted = delete_course(db, course_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    return {"message": "Course deleted successfully"}


# =========================================================
# ASSIGN TEACHERS TO COURSE (Admin only)
# =========================================================

@router.post("/{course_id}/teachers")
def assign_teachers(
    course_id: int,
    assignment: CourseAssignTeachers,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    try:
        teachers = assign_teachers_to_course(db, course_id, assignment.teacher_ids)
        return {
            "message": "Teachers assigned successfully",
            "course_id": course_id,
            "teachers": [
                {
                    "teacher_id": t.teacher_id,
                    "name": t.name,
                    "specialization": t.specialization
                }
                for t in teachers
            ]
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e


# =========================================================
# PUBLISH COURSE (Admin or Teacher)
# =========================================================

@router.put("/{course_id}/publish", response_model=CourseResponse)
def publish_course_endpoint(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher"))
):
    try:
        published = publish_course(db, course_id, current_user.uid)
        return _build_course_response(db, published)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e


# =========================================================
# GET COURSES FOR A SPECIFIC TEACHER
# =========================================================

@router.get("/teacher/{teacher_id}", response_model=list[CourseResponse])
def get_courses_by_teacher(
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    courses = get_teacher_courses(db, teacher_id)
    return [_build_course_response(db, c) for c in courses]