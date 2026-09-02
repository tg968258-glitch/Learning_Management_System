import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from Backend.database import get_db
from Backend.src.core.auth_dependency import (
    get_current_user,
    require_roles,
)
from Backend.src.core.cache import CACHE_TTL, redis_client
from Backend.src.models.user import User
from Backend.src.schemas.students import StudentUpdate
from Backend.src.services.student_service import (
    delete_student,
    get_all_students,
    get_student,
    get_student_by_uid,
    update_student,
)

router = APIRouter(
    prefix="/students",
    tags=["Students"]
)


# =========================================================
# CACHE HELPER
# =========================================================

def _clear_student_cache():
    """Delete all cached student results and profiles."""
    keys = list(redis_client.scan_iter(match="students:*")) + list(redis_client.scan_iter(match="studentProfile:*"))
    deleted_count = 0
    for key in set(keys):
        redis_client.delete(key)
        deleted_count += 1
    print(f"STUDENT CACHE CLEARED: {deleted_count} key(s)")


def _build_student_dict(s) -> dict:
    return {
        "student_id": s.student_id,
        "uid": s.uid,
        "name": s.name,
        "date_of_birth": s.date_of_birth.isoformat() if hasattr(s.date_of_birth, "isoformat") else s.date_of_birth,
        "gender": s.gender,
        "phone_number": s.phone_number,
    }


@router.get("/")
def get_students(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin", "teacher")
    )
):
    cache_key = "students:all"

    cached = redis_client.get(cache_key)
    if cached:
        print(f"CACHE HIT: {cache_key}")
        return json.loads(cached)

    print(f"CACHE MISS: {cache_key}")
    students = get_all_students(db)
    response = [_build_student_dict(s) for s in students]

    redis_client.setex(
        cache_key,
        CACHE_TTL,
        json.dumps(response, default=str)
    )
    print(f"CACHE CREATED: {cache_key}")
    return response


@router.get("/me")
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("student")
    )
):
    cache_key = f"studentProfile:uid:{current_user.uid}"

    cached = redis_client.get(cache_key)
    if cached:
        print(f"CACHE HIT: {cache_key}")
        return {
            "student": json.loads(cached)
        }

    print(f"CACHE MISS: {cache_key}")
    try:
        student = get_student_by_uid(
            db,
            current_user.uid
        )

        response = _build_student_dict(student)
        redis_client.setex(
            cache_key,
            CACHE_TTL,
            json.dumps(response, default=str)
        )
        print(f"CACHE CREATED: {cache_key}")

        return {
            "student": response
        }

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        ) from e


@router.get("/{student_id}")
def get_single_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):
    if student_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="Student ID must be positive"
        )

    cache_key = f"studentProfile:id:{student_id}"

    cached = redis_client.get(cache_key)
    if cached:
        print(f"CACHE HIT: {cache_key}")
        student_dict = json.loads(cached)
        if (
            current_user.role == "student"
            and student_dict.get("uid") != current_user.uid
        ):
            raise HTTPException(
                status_code=403,
                detail="You can only view your own student profile"
            )
        return student_dict

    print(f"CACHE MISS: {cache_key}")
    student = get_student(
        db,
        student_id
    )

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    # Student can only view their own profile
    if (
        current_user.role == "student"
        and student.uid != current_user.uid
    ):
        raise HTTPException(
            status_code=403,
            detail="You can only view your own student profile"
        )

    response = _build_student_dict(student)
    redis_client.setex(
        cache_key,
        CACHE_TTL,
        json.dumps(response, default=str)
    )
    print(f"CACHE CREATED: {cache_key}")

    return response


@router.put("/me")
def update_my_profile(
    student: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("student")
    )
):
    try:
        current_student = get_student_by_uid(
            db,
            current_user.uid
        )

        updated_student = update_student(
            db,
            current_student.student_id,
            student.model_dump(
                exclude_unset=True
            )
        )

        _clear_student_cache()
        return {
            "message": "Profile updated successfully",
            "student": _build_student_dict(updated_student)
        }

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        ) from e


@router.put("/{student_id}")
def update_existing_student(
    student_id: int,
    student_data: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin")
    )
):
    if student_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="Student ID must be positive"
        )

    result = update_student(
        db,
        student_id,
        student_data.model_dump(
            exclude_unset=True
        )
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    _clear_student_cache()
    return {
        "message": "Student updated successfully",
        "student": _build_student_dict(result)
    }


@router.delete("/{student_id}")
def delete_existing_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin")
    )
):
    if student_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="Student ID must be positive"
        )

    result = delete_student(
        db,
        student_id
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    _clear_student_cache()
    return {
        "message": "Student deleted successfully"
    }