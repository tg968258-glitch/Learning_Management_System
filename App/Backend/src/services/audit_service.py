from datetime import date, datetime, time, timedelta

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
    from_date: date | None = None,
    to_date: date | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[AuditLog], int]:
    from_datetime = datetime.combine(from_date, time.min) if from_date else None
    # Use an exclusive upper bound so every timestamp on the selected To Date is included.
    to_datetime = datetime.combine(to_date + timedelta(days=1), time.min) if to_date else None
    return AuditRepository.get_all(
        db,
        uid=uid,
        entity_type=entity_type,
        from_datetime=from_datetime,
        to_datetime=to_datetime,
        page=page,
        page_size=page_size,
    )
