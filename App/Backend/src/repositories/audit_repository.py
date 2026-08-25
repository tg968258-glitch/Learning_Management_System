from datetime import datetime
from sqlalchemy.orm import Session

from Backend.src.models.audit_log import AuditLog


class AuditRepository:
    @staticmethod
    def get_all(
        db: Session,
        uid: str | None = None,
        entity_type: str | None = None,
        limit: int = 100
    ) -> list[AuditLog]:
        query = db.query(AuditLog)
        if uid:
            query = query.filter(AuditLog.uid == uid)
        if entity_type:
            query = query.filter(AuditLog.entity_type == entity_type)
        return query.order_by(AuditLog.created_at.desc()).limit(limit).all()

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
