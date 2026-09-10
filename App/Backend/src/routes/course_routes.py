import json

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from Backend.database import get_db
from Backend.src.core.auth_dependency import get_current_user, require_roles
from Backend.src.core.course_access import accessible_course_ids, require_course_access
from Backend.src.core.cache import CACHE_TTL, redis_client
from Backend.src.models.user import User
from Backend.src.models.course import Course
from Backend.src.models.enrollment import Enrollment
from Backend.src.models.lesson import Lesson
from Backend.src.models.module import Module
from Backend.src.models.student import Student
from Backend.src.models.teacher import Teacher
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
    remove_teacher_from_course,
    update_course,
)
from Backend.src.services.progress_service import get_course_progress_summary


router = APIRouter(
    prefix="/courses",
    tags=["Courses"]
)


# =========================================================
# CACHE HELPER
# =========================================================

def _clear_course_list_cache():
    """
    Delete all cached course-list results.

    Examples:
    courses:all:all
    courses:draft:all
    courses:active:Programming
    """

    keys = redis_client.scan_iter(match="courses:*")

    deleted_count = 0

    for key in keys:
        redis_client.delete(key)
        deleted_count += 1

    print(
        f"COURSE LIST CACHE CLEARED: "
        f"{deleted_count} key(s)"
    )


def _clear_teacher_assignment_cache():
    """Teacher assignment status is derived from course course-teacher rows."""
    for pattern in ("teachers:*", "teacherProfile:*"):
        for key in redis_client.scan_iter(match=pattern):
            redis_client.delete(key)


# =========================================================
# BUILD COURSE RESPONSE
# =========================================================

def _build_course_response(
    db: Session,
    course: Course,
    current_user: User | None = None,
    include_modules: bool = False,
) -> dict:

    teachers = get_course_teachers(
        db,
        course.course_id
    )

    modules = (
        db.query(Module)
        .filter(Module.course_id == course.course_id)
        .order_by(Module.module_id)
        .all()
    )
    lessons = (
        db.query(Lesson)
        .join(Module, Module.module_id == Lesson.module_id)
        .filter(Module.course_id == course.course_id)
        .order_by(Lesson.module_id, Lesson.lesson_id)
        .all()
    )
    lessons_by_module: dict[int, list[Lesson]] = {}
    for lesson in lessons:
        lessons_by_module.setdefault(lesson.module_id, []).append(lesson)

    enrollment_count = (
        db.query(Enrollment)
        .filter(Enrollment.course_id == course.course_id, Enrollment.status == "active")
        .count()
    )

    is_enrolled = False
    completed_lessons = None
    overall_progress = None
    if current_user and current_user.role == "student":
        student = db.query(Student).filter(Student.uid == current_user.uid).first()
        if student:
            is_enrolled = db.query(Enrollment).filter(
                Enrollment.student_id == student.student_id,
                Enrollment.course_id == course.course_id,
                Enrollment.status == "active",
            ).first() is not None
        if student and is_enrolled:
            summary = get_course_progress_summary(db, student.student_id, course.course_id)
            completed_lessons = summary["completed_lessons"]
            overall_progress = summary["overall_progress_percentage"]

    response = {
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
        "module_count": len(modules),
        "lesson_count": len(lessons),
        "enrollment_count": enrollment_count,
        "is_enrolled": is_enrolled,
        "completed_lessons": completed_lessons,
        "overall_progress_percentage": overall_progress,
    }

    if include_modules:
        response["modules"] = [
            {
                "module_id": module.module_id,
                "course_id": module.course_id,
                "module_name": module.module_name,
                "description": module.description,
                "is_published": module.is_published,
                "lessons": [
                    {
                        "lesson_id": lesson.lesson_id,
                        "module_id": lesson.module_id,
                        "lesson_title": lesson.lesson_title,
                        "is_published": lesson.is_published,
                    }
                    for lesson in lessons_by_module.get(module.module_id, [])
                ],
            }
            for module in modules
        ]

    return response


# =========================================================
# LIST COURSES
# =========================================================

@router.get(
    "/",
    response_model=list[CourseResponse]
)
def list_courses(
    status: str | None = Query(
        None,
        description="Filter by status (e.g. active, draft)"
    ),
    category: str | None = Query(
        None,
        description="Filter by category"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Students browse the complete published catalog before enrolling.
    if current_user.role == "student":
        courses = get_all_courses(db, status="active", category=category)
        return [_build_course_response(db, course, current_user) for course in courses]

    allowed_course_ids = accessible_course_ids(db, current_user)
    if allowed_course_ids is not None:
        courses = get_all_courses(db, status=status, category=category)
        return [
            _build_course_response(db, course, current_user)
            for course in courses
            if course.course_id in allowed_course_ids
        ]

    # -----------------------------------------------------
    # Create cache key using filters
    # -----------------------------------------------------

    status_key = status or "all"
    category_key = category or "all"

    cache_key = (
        f"courses:v3:{status_key}:{category_key}"
    )

    # -----------------------------------------------------
    # STEP 1: Check Valkey
    # -----------------------------------------------------

    cached_courses = redis_client.get(
        cache_key
    )

    if cached_courses:

        print(
            f"CACHE HIT: {cache_key}"
        )

        return json.loads(
            cached_courses
        )

    print(
        f"CACHE MISS: {cache_key}"
    )

    # -----------------------------------------------------
    # STEP 2: Fetch courses from PostgreSQL
    # -----------------------------------------------------

    courses = get_all_courses(
        db,
        status=status,
        category=category
    )

    response = [
        _build_course_response(
            db,
            course,
            current_user,
        )
        for course in courses
    ]

    # -----------------------------------------------------
    # STEP 3: Store result in Valkey
    # -----------------------------------------------------

    redis_client.setex(
        cache_key,
        CACHE_TTL,
        json.dumps(
            response,
            default=str
        )
    )

    print(
        f"CACHE CREATED: {cache_key}"
    )

    return response


# =========================================================
# GET COURSES FOR THE CURRENT STUDENT OR TEACHER
# Keep this static route before /{course_id}.
# =========================================================

@router.get(
    "/my-courses",
    response_model=list[CourseResponse]
)
def get_my_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("student", "teacher"))
):

    allowed_course_ids = accessible_course_ids(db, current_user) or set()
    if not allowed_course_ids:
        return []

    courses = (
        db.query(Course)
        .filter(Course.course_id.in_(allowed_course_ids))
        .order_by(Course.course_id)
        .all()
    )
    response = []
    for course in courses:
        course_data = _build_course_response(db, course, current_user)
        response.append(course_data)
    return response


# =========================================================
# GET SINGLE COURSE
# =========================================================

@router.get(
    "/{course_id}",
    response_model=CourseResponse
)
def get_course_by_id(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    if course_id <= 0:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course ID must be positive"
        )

    # Students may view published metadata before enrolling. Course content
    # remains protected by the module/lesson/etc. access checks.
    if current_user.role == "student":
        course = get_course(db, course_id)
        if not course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
        allowed_course_ids = accessible_course_ids(db, current_user) or set()
        if course.status != "active":
            require_course_access(db, current_user, course_id)
        return _build_course_response(
            db,
            course,
            current_user,
            include_modules=course_id in allowed_course_ids,
        )

    require_course_access(db, current_user, course_id)

    course = get_course(
        db,
        course_id
    )

    if not course:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    response = _build_course_response(
        db,
        course,
        current_user,
        include_modules=True,
    )
    return response


# =========================================================
# CREATE COURSE
# Admin or Teacher
# =========================================================

@router.post(
    "/",
    response_model=CourseResponse,
    status_code=status.HTTP_201_CREATED
)
def add_new_course(
    course_in: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "admin",
            "teacher"
        )
    )
):

    try:

        created = create_course(
            db=db,
            course_data=course_in.model_dump(),
            created_by_uid=current_user.uid
        )

        # A new course changes course lists
        _clear_course_list_cache()

        return _build_course_response(
            db,
            created
        )

    except ValueError as e:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e


# =========================================================
# UPDATE COURSE
# Admin or Teacher
# =========================================================

@router.put(
    "/{course_id}",
    response_model=CourseResponse
)
def update_existing_course(
    course_id: int,
    course_in: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "admin",
            "teacher"
        )
    )
):

    if course_id <= 0:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course ID must be positive"
        )

    updated = update_course(
        db=db,
        course_id=course_id,
        updated_data=course_in.model_dump(
            exclude_unset=True
        )
    )

    if not updated:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    # -----------------------------------------------------
    # Clear individual course cache
    # -----------------------------------------------------

    cache_key = f"course:{course_id}"

    redis_client.delete(
        cache_key
    )

    # -----------------------------------------------------
    # Clear course-list caches
    # -----------------------------------------------------

    _clear_course_list_cache()

    print(
        f"CACHE DELETED AFTER UPDATE: "
        f"{cache_key}"
    )

    return _build_course_response(
        db,
        updated
    )


# =========================================================
# DELETE COURSE
# Admin only
# =========================================================

@router.delete(
    "/{course_id}"
)
def remove_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin")
    )
):

    if course_id <= 0:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course ID must be positive"
        )

    deleted = delete_course(
        db,
        course_id
    )

    if not deleted:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    # -----------------------------------------------------
    # Delete individual course cache
    # -----------------------------------------------------

    cache_key = f"course:{course_id}"

    redis_client.delete(
        cache_key
    )

    # -----------------------------------------------------
    # Delete course-list caches
    # -----------------------------------------------------

    _clear_course_list_cache()

    print(
        f"CACHE DELETED AFTER COURSE DELETE: "
        f"{cache_key}"
    )

    return {
        "message": "Course deleted successfully"
    }


# =========================================================
# ASSIGN TEACHERS TO COURSE
# Admin only
# =========================================================

@router.post(
    "/{course_id}/teachers"
)
def assign_teachers(
    course_id: int,
    assignment: CourseAssignTeachers,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin")
    )
):

    try:

        teachers = assign_teachers_to_course(
            db,
            course_id,
            assignment.teacher_ids
        )

        # -------------------------------------------------
        # Clear individual course cache
        # -------------------------------------------------

        cache_key = f"course:{course_id}"

        redis_client.delete(
            cache_key
        )

        # -------------------------------------------------
        # Clear course-list caches
        # -------------------------------------------------

        _clear_course_list_cache()
        _clear_teacher_assignment_cache()

        print(
            f"CACHE DELETED AFTER "
            f"TEACHER ASSIGNMENT: {cache_key}"
        )

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


@router.delete("/{course_id}/teachers/{teacher_id}")
def remove_assigned_teacher(
    course_id: int,
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    try:
        removed = remove_teacher_from_course(db, course_id, teacher_id)
        if not removed:
            raise HTTPException(status_code=404, detail="Teacher is not assigned to this course")
        redis_client.delete(f"course:{course_id}")
        _clear_course_list_cache()
        _clear_teacher_assignment_cache()
        return {"message": "Teacher removed from course successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


# =========================================================
# PUBLISH COURSE
# Admin or Teacher
# =========================================================

@router.put(
    "/{course_id}/publish",
    response_model=CourseResponse
)
def publish_course_endpoint(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "admin",
            "teacher"
        )
    )
):

    try:

        published = publish_course(
            db,
            course_id,
            current_user.uid
        )

        # -------------------------------------------------
        # Clear individual course cache
        # -------------------------------------------------

        cache_key = f"course:{course_id}"

        redis_client.delete(
            cache_key
        )

        # -------------------------------------------------
        # Clear course-list caches
        # -------------------------------------------------

        _clear_course_list_cache()

        print(
            f"CACHE DELETED AFTER PUBLISH: "
            f"{cache_key}"
        )

        return _build_course_response(
            db,
            published
        )

    except ValueError as e:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e


# =========================================================
# GET COURSES FOR A SPECIFIC TEACHER
# =========================================================

@router.get(
    "/teacher/{teacher_id}",
    response_model=list[CourseResponse]
)
def get_courses_by_teacher(
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    courses = get_teacher_courses(
        db,
        teacher_id
    )

    return [
        _build_course_response(
            db,
            course
        )
        for course in courses
    ]
