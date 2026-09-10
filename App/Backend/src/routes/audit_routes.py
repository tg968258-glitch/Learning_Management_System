from datetime import date
from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from Backend.database import get_db
from Backend.src.core.auth_dependency import require_roles
from Backend.src.models.user import User
from Backend.src.models.student import Student
from Backend.src.models.teacher import Teacher
from Backend.src.schemas.notifications import AuditLogPageResponse
from Backend.src.services.audit_service import get_audit_logs

router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"]
)


@router.get("/", response_model=AuditLogPageResponse)
def list_system_audit_logs(
    uid: str | None = Query(None, description="Filter by user UID"),
    entity_type: str | None = Query(None, description="Filter by entity type (e.g. course, quiz, submission)"),
    from_date: date | None = Query(None, description="Inclusive start date (YYYY-MM-DD)"),
    to_date: date | None = Query(None, description="Inclusive end date (YYYY-MM-DD)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    if from_date and to_date and from_date > to_date:
        raise HTTPException(status_code=400, detail="From Date cannot be later than To Date.")

    logs, total = get_audit_logs(
        db,
        uid=uid,
        entity_type=entity_type,
        from_date=from_date,
        to_date=to_date,
        page=page,
        page_size=page_size,
    )

    uids = {log.uid for log in logs}
    users = db.query(User).filter(User.uid.in_(uids)).all() if uids else []
    user_by_uid = {user.uid: user for user in users}
    student_names = {
        profile.uid: profile.name
        for profile in db.query(Student).filter(Student.uid.in_(uids)).all()
    } if uids else {}
    teacher_names = {
        profile.uid: profile.name
        for profile in db.query(Teacher).filter(Teacher.uid.in_(uids)).all()
    } if uids else {}

    response = []
    for log in logs:
        user = user_by_uid.get(log.uid)
        name = (
            student_names.get(log.uid)
            if user and user.role == "student"
            else teacher_names.get(log.uid)
            if user and user.role == "teacher"
            else user.username
            if user
            else "System"
        )
        response.append({
            "audit_id": log.audit_id,
            "uid": log.uid,
            "user_name": name or (user.username if user else "System"),
            "role": user.role if user else "system",
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "status": "success",
            "created_at": log.created_at,
        })
    return {
        "items": response,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": ceil(total / page_size) if total else 0,
    }
