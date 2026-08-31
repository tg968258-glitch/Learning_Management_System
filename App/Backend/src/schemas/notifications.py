from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from Backend.src.utils.input_validator import is_empty

# =========================================================
# NOTIFICATION SCHEMAS
# =========================================================

class NotificationBase(BaseModel):
    uid: str
    session_id: int | None = None
    assignment_id: int | None = None
    notification_type: str
    title: str | None = None
    message: str

    @field_validator("notification_type")
    @classmethod
    def validate_type(cls, value: str) -> str:
        value = value.strip()
        if is_empty(value):
            raise ValueError("Notification type cannot be empty")
        return value

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        value = value.strip()
        if is_empty(value):
            raise ValueError("Message cannot be empty")
        return value


class NotificationCreate(NotificationBase):
    pass


class NotificationResponse(BaseModel):
    notification_id: int
    uid: str
    session_id: int | None = None
    assignment_id: int | None = None
    notification_type: str
    title: str | None = None
    message: str
    status: str
    is_read: bool
    sent_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# AUDIT LOG SCHEMAS
# =========================================================

class AuditLogResponse(BaseModel):
    audit_id: int
    uid: str
    action: str
    entity_type: str
    entity_id: str | None = None

    model_config = ConfigDict(from_attributes=True)
