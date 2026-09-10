from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

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

    @field_validator("question_type")
    @classmethod
    def validate_question_type(cls, value: str) -> str:
        normalized = value.strip().lower()
        aliases = {"multiple_choice": "mcq"}
        normalized = aliases.get(normalized, normalized)
        if normalized not in ("mcq", "true_false", "single_choice"):
            raise ValueError("Unsupported question type")
        return normalized

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

    @model_validator(mode="after")
    def validate_options(self):
        if len(self.options) < 2 or len(self.options) > 10:
            raise ValueError("A question must have between 2 and 10 options")
        normalized = [option.option_text.casefold() for option in self.options]
        if len(normalized) != len(set(normalized)):
            raise ValueError("Question options must be unique")
        if sum(option.is_correct for option in self.options) != 1:
            raise ValueError("Exactly one option must be marked correct")
        return self


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

    @model_validator(mode="after")
    def validate_marks_range(self):
        if self.passing_marks > self.max_marks:
            raise ValueError("Passing marks cannot exceed maximum marks")
        return self

    @field_validator("duration_minutes")
    @classmethod
    def validate_duration(cls, value: int | None) -> int | None:
        if value is not None and not 1 <= value <= 600:
            raise ValueError("Duration must be between 1 and 600 minutes")
        return value

    @field_validator("max_attempts")
    @classmethod
    def validate_attempts(cls, value: int) -> int:
        if not 1 <= value <= 100:
            raise ValueError("Maximum attempts must be between 1 and 100")
        return value

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
    course_id: int

    @field_validator("course_id")
    @classmethod
    def validate_course_id(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("Course ID must be positive")
        return value


class QuizUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    max_marks: float | None = None
    passing_marks: float | None = None
    duration_minutes: int | None = None
    max_attempts: int | None = None
    is_published: bool | None = None

    @field_validator("max_marks")
    @classmethod
    def validate_max_marks(cls, value: float | None) -> float | None:
        if value is not None and value <= 0:
            raise ValueError("Max marks must be positive")
        return value

    @field_validator("passing_marks")
    @classmethod
    def validate_passing_marks(cls, value: float | None) -> float | None:
        if value is not None and value < 0:
            raise ValueError("Passing marks cannot be negative")
        return value

    @field_validator("duration_minutes")
    @classmethod
    def validate_duration(cls, value: int | None) -> int | None:
        if value is not None and not 1 <= value <= 600:
            raise ValueError("Duration must be between 1 and 600 minutes")
        return value

    @field_validator("max_attempts")
    @classmethod
    def validate_attempts(cls, value: int | None) -> int | None:
        if value is not None and not 1 <= value <= 100:
            raise ValueError("Maximum attempts must be between 1 and 100")
        return value


class QuizResponse(BaseModel):
    quiz_id: int
    course_id: int
    lesson_id: int | None = None
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

    @field_validator("question_id", "selected_option_id")
    @classmethod
    def validate_ids(cls, value: int | None) -> int | None:
        if value is not None and value <= 0:
            raise ValueError("Question and option IDs must be positive")
        return value


class QuizSubmitRequest(BaseModel):
    answers: list[SubmitAnswerItem]

    @model_validator(mode="after")
    def validate_answers(self):
        if not self.answers:
            raise ValueError("At least one answer is required")
        question_ids = [answer.question_id for answer in self.answers]
        if len(question_ids) != len(set(question_ids)):
            raise ValueError("Each question may be answered only once")
        return self


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
