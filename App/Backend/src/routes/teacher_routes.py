import json
from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import String, cast, or_
from sqlalchemy.orm import Session

from Backend.database import get_db
from Backend.src.core.auth_dependency import (
    get_current_user,
    require_roles,
)
from Backend.src.core.cache import CACHE_TTL, redis_client
from Backend.src.models.user import User
from Backend.src.models.course import CourseTeacher
from Backend.src.schemas.teachers import TeacherUpdate
from Backend.src.schemas.dashboard import TeacherDashboardStats
from Backend.src.services.teacher_service import (
    delete_teacher,
    get_all_teachers,
    get_teacher,
    get_teacher_by_uid,
    get_teacher_dashboard_stats,
    update_teacher,
)

router = APIRouter(
    prefix="/teachers",
    tags=["Teachers"]
)

dashboard_router = APIRouter(
    prefix="/teacher",
    tags=["Teacher Dashboard"]
)


@dashboard_router.get("/dashboard/stats", response_model=TeacherDashboardStats)
def teacher_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("teacher"))
):
    return get_teacher_dashboard_stats(db, current_user.uid)


# =========================================================
# CACHE HELPER
# =========================================================

def _clear_teacher_cache():
    """Delete all cached teacher results and profiles."""
    keys = list(redis_client.scan_iter(match="teachers:*")) + list(redis_client.scan_iter(match="teacherProfile:*"))
    deleted_count = 0
    for key in set(keys):
        redis_client.delete(key)
        deleted_count += 1
    print(f"TEACHER CACHE CLEARED: {deleted_count} key(s)")


def _build_teacher_dict(db: Session, t) -> dict:
    user = db.query(User).filter(User.uid == t.uid).first()
    assignment_count = (
        db.query(CourseTeacher)
        .filter(CourseTeacher.teacher_id == t.teacher_id)
        .count()
    )
    return {
        "teacher_id": t.teacher_id,
        "uid": t.uid,
        "name": t.name,
        "phone_number": t.phone_number,
        "specialization": t.specialization,
        "qualification": t.qualification,
        "experience": t.experience,
        "email": user.email if user else None,
        "invitation_status": "Accepted",
        "assignment_status": "Assigned" if assignment_count else "Awaiting Course Assignment",
        "assigned_course_count": assignment_count,
    }


@router.get("/page")
def get_teachers_page(
    page: int = Query(1, ge=1),
    page_size: int = Query(6, ge=1, le=100),
    search: str | None = Query(None, max_length=150),
    specialization: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher")),
):
    query = db.query(Teacher).join(User, User.uid == Teacher.uid)
    if specialization:
        query = query.filter(Teacher.specialization == specialization)
    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(or_(
            Teacher.name.ilike(term), User.email.ilike(term), Teacher.uid.ilike(term),
            Teacher.specialization.ilike(term), cast(Teacher.teacher_id, String).ilike(term),
        ))
    total = query.count()
    rows = query.order_by(Teacher.name).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "items": [_build_teacher_dict(db, row) for row in rows],
        "page": page, "page_size": page_size, "total": total,
        "total_pages": ceil(total / page_size) if total else 0,
    }


@router.get("/")
def get_teachers(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin", "teacher")
    )
):
    teachers = get_all_teachers(db)
    return [_build_teacher_dict(db, t) for t in teachers]


@router.get("/me")
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("teacher")
    )
):
    cache_key = f"teacherProfile:uid:{current_user.uid}"

    cached = redis_client.get(cache_key)
    if cached:
        print(f"CACHE HIT: {cache_key}")
        return {
            "teacher": json.loads(cached)
        }

    print(f"CACHE MISS: {cache_key}")
    teacher = get_teacher_by_uid(
        db,
        current_user.uid
    )

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher profile not found"
        )

    response = _build_teacher_dict(db, teacher)
    redis_client.setex(
        cache_key,
        CACHE_TTL,
        json.dumps(response, default=str)
    )
    print(f"CACHE CREATED: {cache_key}")

    return {
        "teacher": response
    }


@router.put("/me")
def update_my_profile(
    teacher: TeacherUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("teacher")
    )
):
    existing = get_teacher_by_uid(
        db,
        current_user.uid
    )

    if not existing:
        raise HTTPException(
            status_code=404,
            detail="Teacher profile not found"
        )

    updated_teacher = update_teacher(
        db,
        existing.teacher_id,
        teacher.model_dump(
            exclude_unset=True
        )
    )

    _clear_teacher_cache()

    return {
        "message": "Teacher profile updated successfully",
        "teacher": _build_teacher_dict(db, updated_teacher)
    }


@router.get("/{teacher_id}")
def get_teacher_by_id(
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):
    if teacher_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="Teacher ID must be positive"
        )

    cache_key = f"teacherProfile:id:{teacher_id}"

    cached = redis_client.get(cache_key)
    if cached:
        print(f"CACHE HIT: {cache_key}")
        teacher_dict = json.loads(cached)
        if (
            current_user.role == "teacher"
            and teacher_dict.get("uid") != current_user.uid
        ):
            raise HTTPException(
                status_code=403,
                detail="You can only view your own teacher profile"
            )
        return teacher_dict

    print(f"CACHE MISS: {cache_key}")
    teacher = get_teacher(
        db,
        teacher_id
    )

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher not found"
        )

    if (
        current_user.role == "teacher"
        and teacher.uid != current_user.uid
    ):
        raise HTTPException(
            status_code=403,
            detail="You can only view your own teacher profile"
        )

    response = _build_teacher_dict(db, teacher)
    redis_client.setex(
        cache_key,
        CACHE_TTL,
        json.dumps(response, default=str)
    )
    print(f"CACHE CREATED: {cache_key}")

    return response


@router.put("/{teacher_id}")
def edit_teacher(
    teacher_id: int,
    teacher: TeacherUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin")
    )
):
    if teacher_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="Teacher ID must be positive"
        )

    updated_teacher = update_teacher(
        db,
        teacher_id,
        teacher.model_dump(
            exclude_unset=True
        )
    )

    if not updated_teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher not found"
        )

    _clear_teacher_cache()
    return {
        "message": "Teacher updated successfully",
        "teacher": _build_teacher_dict(db, updated_teacher)
    }


@router.delete("/{teacher_id}")
def remove_teacher(
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin")
    )
):
    if teacher_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="Teacher ID must be positive"
        )

    deleted_teacher = delete_teacher(
        db,
        teacher_id
    )

    if not deleted_teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher not found"
        )

    _clear_teacher_cache()
    return {
        "message": "Teacher deleted successfully"
    }
