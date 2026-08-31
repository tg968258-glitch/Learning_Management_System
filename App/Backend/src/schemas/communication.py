from datetime import date, datetime, time
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, field_validator

from Backend.src.utils.input_validator import is_empty, validate_length
from Backend.src.utils.numeric_validator import is_positive


# =========================================================
# CLASS SESSIONS SCHEMAS
# =========================================================

def validate_meeting_link(value: str | None) -> str | None:
    if value is None:
        return None

    value = value.strip()

    if is_empty(value):
        return None

    parsed_url = urlparse(value)

    if parsed_url.scheme not in ("http", "https"):
        raise ValueError(
            "Meeting link must start with http:// or https://"
        )

    hostname = (parsed_url.hostname or "").lower()

    valid_domain = (
        hostname == "meet.google.com"
        or hostname == "zoom.us"
        or hostname.endswith(".zoom.us")
        or hostname == "teams.microsoft.com"
    )

    if not valid_domain:
        raise ValueError(
            "Only Google Meet, Zoom, and Microsoft Teams links are allowed"
        )

    return value


class ClassSessionBase(BaseModel):
    course_id: int
    teacher_id: int | None = None
    session_date: date
    start_time: time | None = None
    end_time: time | None = None
    topic: str | None = None
    meeting_link: str | None = None

    @field_validator("course_id")
    @classmethod
    def validate_course_id(cls, value: int) -> int:
        if not is_positive(value):
            raise ValueError("Course ID must be positive")
        return value

    @field_validator("teacher_id")
    @classmethod
    def validate_teacher_id(cls, value: int | None) -> int | None:
        if value is not None and not is_positive(value):
            raise ValueError("Teacher ID must be positive")
        return value

    @field_validator("topic")
    @classmethod
    def validate_topic(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if is_empty(value):
            return None

        if not validate_length(value, 2, 200):
            raise ValueError(
                "Topic must be between 2 and 200 characters"
            )

        return value

    @field_validator("meeting_link")
    @classmethod
    def check_meeting_link(cls, value: str | None) -> str | None:
        return validate_meeting_link(value)


class ClassSessionCreate(ClassSessionBase):
    pass


class ClassSessionUpdate(BaseModel):
    teacher_id: int | None = None
    session_date: date | None = None
    start_time: time | None = None
    end_time: time | None = None
    topic: str | None = None
    meeting_link: str | None = None

    @field_validator("teacher_id")
    @classmethod
    def validate_teacher_id(cls, value: int | None) -> int | None:
        if value is not None and not is_positive(value):
            raise ValueError("Teacher ID must be positive")
        return value

    @field_validator("topic")
    @classmethod
    def validate_topic(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if is_empty(value):
            return None

        if not validate_length(value, 2, 200):
            raise ValueError(
                "Topic must be between 2 and 200 characters"
            )

        return value

    @field_validator("meeting_link")
    @classmethod
    def check_meeting_link(cls, value: str | None) -> str | None:
        return validate_meeting_link(value)


class ClassSessionResponse(BaseModel):
    session_id: int
    course_id: int
    teacher_id: int | None = None
    session_date: date
    start_time: time | None = None
    end_time: time | None = None
    topic: str | None = None
    meeting_link: str | None = None
    teacher_name: str | None = None
    course_name: str | None = None

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# DISCUSSIONS SCHEMAS
# =========================================================

class DiscussionBase(BaseModel):
    course_id: int
    lesson_id: int | None = None
    parent_id: int | None = None
    message: str

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        value = value.strip()

        if is_empty(value):
            raise ValueError("Discussion message cannot be empty")

        return value


class DiscussionCreate(DiscussionBase):
    pass


class DiscussionUpdate(BaseModel):
    message: str

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        value = value.strip()

        if is_empty(value):
            raise ValueError("Discussion message cannot be empty")

        return value


class DiscussionResponse(BaseModel):
    discussion_id: int
    course_id: int
    lesson_id: int | None = None
    sender_uid: str
    parent_id: int | None = None
    message: str
    sender_name: str | None = None
    sender_role: str | None = None

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# ANNOUNCEMENTS SCHEMAS
# =========================================================

class AnnouncementBase(BaseModel):
    course_id: int
    session_id: int | None = None
    title: str
    message: str

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()

        if is_empty(value):
            raise ValueError("Title cannot be empty")

        if not validate_length(value, 2, 150):
            raise ValueError(
                "Title must be between 2 and 150 characters"
            )

        return value

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        value = value.strip()

        if is_empty(value):
            raise ValueError(
                "Announcement message cannot be empty"
            )

        return value


class AnnouncementCreate(AnnouncementBase):
    pass


class AnnouncementUpdate(BaseModel):
    title: str | None = None
    message: str | None = None


class AnnouncementResponse(BaseModel):
    announcement_id: int
    course_id: int
    session_id: int | None = None
    created_by: str
    title: str
    message: str

    model_config = ConfigDict(from_attributes=True)