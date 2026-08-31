from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from Backend.src.utils.input_validator import is_empty, validate_length
from Backend.src.utils.numeric_validator import is_positive

# =========================================================
# QUESTION OPTION SCHEMAS
# =========================================================

class OptionBase(BaseModel):
    option_text: str
    is_correct: bool = False

    @field_validator("option_text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        value = value.strip()
        if is_empty(value):
            raise ValueError("Option text cannot be empty")
        return value


class OptionCreate(OptionBase):
    pass


class OptionResponse(BaseModel):
    option_id: int
    question_id: int
    option_text: str
    is_correct: bool | None = None  # Hidden from students during quiz

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# QUESTION SCHEMAS
# =========================================================

class QuestionBase(BaseModel):
    question_text: str
    question_type: str = "mcq"  # "mcq", "true_false", "single_choice"
    marks: float = 1.0

    @field_validator("question_text")
    @classmethod
    def validate_question(cls, value: str) -> str:
        value = value.strip()
        if is_empty(value):
            raise ValueError("Question text cannot be empty")
        return value

    @field_validator("marks")
    @classmethod
    def validate_marks(cls, value: float) -> float:
        if not is_positive(value):
            raise ValueError("Question marks must be positive")
        return round(value, 2)


class QuestionCreate(QuestionBase):
    options: list[OptionCreate]


class QuestionResponse(BaseModel):
    question_id: int
    quiz_id: int
    question_text: str
    question_type: str
    marks: float
    options: list[OptionResponse] = []

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# QUIZ SCHEMAS
# =========================================================

class QuizBase(BaseModel):
    title: str
    description: str | None = None
    max_marks: float
    passing_marks: float
    duration_minutes: int | None = None
    max_attempts: int = 1
    is_published: bool = False

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()
        if is_empty(value):
            raise ValueError("Quiz title cannot be empty")
        if not validate_length(value, 2, 150):
            raise ValueError("Quiz title must be between 2 and 150 characters")
        return value

    @field_validator("max_marks")
    @classmethod
    def validate_max_marks(cls, value: float) -> float:
        if not is_positive(value):
            raise ValueError("Max marks must be positive")
        return round(value, 2)

    @field_validator("passing_marks")
    @classmethod
    def validate_passing(cls, value: float) -> float:
        if value < 0:
            raise ValueError("Passing marks cannot be negative")
        return round(value, 2)


class QuizCreate(QuizBase):
    lesson_id: int


class QuizUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    max_marks: float | None = None
    passing_marks: float | None = None
    duration_minutes: int | None = None
    max_attempts: int | None = None
    is_published: bool | None = None


class QuizResponse(BaseModel):
    quiz_id: int
    lesson_id: int
    title: str
    description: str | None = None
    max_marks: float
    passing_marks: float
    duration_minutes: int | None = None
    max_attempts: int
    is_published: bool

    model_config = ConfigDict(from_attributes=True)


class QuizDetailResponse(QuizResponse):
    questions: list[QuestionResponse] = []


# =========================================================
# QUIZ ATTEMPT & ANSWERS SCHEMAS
# =========================================================

class SubmitAnswerItem(BaseModel):
    question_id: int
    selected_option_id: int | None = None


class QuizSubmitRequest(BaseModel):
    answers: list[SubmitAnswerItem]


class StudentAnswerResponse(BaseModel):
    answer_id: int
    attempt_id: int
    question_id: int
    selected_option_id: int | None = None
    marks_awarded: float | None = None

    model_config = ConfigDict(from_attributes=True)


class QuizAttemptResponse(BaseModel):
    attempt_id: int
    quiz_id: int
    student_id: int
    attempt_number: int
    started_at: datetime | None = None
    submitted_at: datetime | None = None
    marks: float | None = None
    status: str
    passed: bool | None = None
    answers: list[StudentAnswerResponse] = []

    model_config = ConfigDict(from_attributes=True)
