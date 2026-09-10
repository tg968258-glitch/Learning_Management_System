from datetime import datetime
from sqlalchemy.orm import Session

from Backend.src.models.audit_log import AuditLog


class AuditRepository:
    @staticmethod
    def get_all(
        db: Session,
        uid: str | None = None,
        entity_type: str | None = None,
        from_datetime: datetime | None = None,
        to_datetime: datetime | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[AuditLog], int]:
        query = db.query(AuditLog)
        if uid:
            query = query.filter(AuditLog.uid == uid)
        if entity_type:
            query = query.filter(AuditLog.entity_type == entity_type)
        if from_datetime:
            query = query.filter(AuditLog.created_at >= from_datetime)
        if to_datetime:
            query = query.filter(AuditLog.created_at < to_datetime)

        total = query.count()
        items = (
            query.order_by(AuditLog.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

    @staticmethod
    def log(
        db: Session,
        uid: str,
        action: str,
        entity_type: str,
        entity_id: str | None = None
    ) -> AuditLog:
        log_entry = AuditLog(
            uid=uid,
            action=action,
            entity_type=entity_type,
            entity_id=str(entity_id) if entity_id is not None else None,
            created_at=datetime.utcnow()
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry
