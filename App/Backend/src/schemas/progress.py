from datetime import date

from pydantic import BaseModel, ConfigDict, field_validator


class LessonProgressUpdate(BaseModel):
    progress_percentage: float
    completed: bool = False

    @field_validator("progress_percentage")
    @classmethod
    def validate_percentage(cls, value: float) -> float:
        if not (0.0 <= value <= 100.0):
            raise ValueError("Progress percentage must be between 0.0 and 100.0")
        return round(value, 2)


class LessonProgressResponse(BaseModel):
    student_id: int
    lesson_id: int
    progress_percentage: float
    completed: bool
    completed_date: date | None = None
    lesson_title: str | None = None

    model_config = ConfigDict(from_attributes=True)


class CourseProgressSummary(BaseModel):
    course_id: int
    course_name: str
    total_lessons: int
    completed_lessons: int
    overall_progress_percentage: float
