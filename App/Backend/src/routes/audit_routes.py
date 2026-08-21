from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from Backend.database import get_db
from Backend.src.core.auth_dependency import require_roles
from Backend.src.models.user import User
from Backend.src.schemas.notifications import AuditLogResponse
from Backend.src.services.audit_service import get_audit_logs

router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"]
)


@router.get("/", response_model=list[AuditLogResponse])
def list_system_audit_logs(
    uid: str | None = Query(None, description="Filter by user UID"),
    entity_type: str | None = Query(None, description="Filter by entity type (e.g. course, quiz, submission)"),
    limit: int = Query(100, ge=1, le=500, description="Max records to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    return get_audit_logs(db, uid=uid, entity_type=entity_type, limit=limit)
