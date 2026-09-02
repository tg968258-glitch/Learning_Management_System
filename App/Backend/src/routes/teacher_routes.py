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
from Backend.src.schemas.teachers import TeacherUpdate
from Backend.src.services.teacher_service import (
    delete_teacher,
    get_all_teachers,
    get_teacher,
    update_teacher,
)

router = APIRouter(
    prefix="/teachers",
    tags=["Teachers"]
)


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


def _build_teacher_dict(t) -> dict:
    return {
        "teacher_id": t.teacher_id,
        "uid": t.uid,
        "name": t.name,
        "phone_number": t.phone_number,
        "specialization": t.specialization,
        "qualification": t.qualification,
        "experience": t.experience,
    }


@router.get("/")
def get_teachers(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin", "teacher")
    )
):
    cache_key = "teachers:all"

    cached = redis_client.get(cache_key)
    if cached:
        print(f"CACHE HIT: {cache_key}")
        return json.loads(cached)

    print(f"CACHE MISS: {cache_key}")
    teachers = get_all_teachers(db)
    response = [_build_teacher_dict(t) for t in teachers]

    redis_client.setex(
        cache_key,
        CACHE_TTL,
        json.dumps(response, default=str)
    )
    print(f"CACHE CREATED: {cache_key}")
    return response


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

    response = _build_teacher_dict(teacher)
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
        "teacher": _build_teacher_dict(updated_teacher)
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