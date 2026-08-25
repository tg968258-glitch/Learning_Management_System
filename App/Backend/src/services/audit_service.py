from sqlalchemy.orm import Session

from Backend.src.models.audit_log import AuditLog
from Backend.src.repositories.audit_repository import AuditRepository
from Backend.src.utils.logger import logger


def log_activity(
    db: Session,
    uid: str,
    action: str,
    entity_type: str,
    entity_id: str | None = None
) -> AuditLog:
    try:
        entry = AuditRepository.log(db, uid, action, entity_type, entity_id)
        return entry
    except Exception as e:
        logger.error(f"Failed to record audit log: {e}")
        raise


def get_audit_logs(
    db: Session,
    uid: str | None = None,
    entity_type: str | None = None,
    limit: int = 100
) -> list[AuditLog]:
    return AuditRepository.get_all(db, uid=uid, entity_type=entity_type, limit=limit)
