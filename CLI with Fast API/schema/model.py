from pydantic import BaseModel, EmailStr, Field


# ---------------- STUDENT ----------------

class StudentCreate(BaseModel):
    name: str
    age: int = Field(..., ge=1, le=100)
    email: EmailStr
    gender: str
    percentage: float = Field(..., ge=0, le=100)
    phone_number: str = Field(..., min_length=10, max_length=10)


class StudentUpdate(BaseModel):
    name: str | None = None
    age: int | None = Field(default=None, ge=1, le=100)
    email: EmailStr | None = None
    gender: str | None = None
    percentage: float | None = Field(default=None, ge=0, le=100)
    phone_number: str | None = Field(default=None, min_length=10, max_length=10)


class StudentResponse(BaseModel):
    student_id: int
    name: str
    age: int
    email: EmailStr
    gender: str
    percentage: float
    phone_number: str


# ---------------- COURSE ----------------

class CourseCreate(BaseModel):
    course_name: str
    trainer: str
    duration: str


class CourseUpdate(BaseModel):
    course_name: str | None = None
    trainer: str | None = None
    duration: str | None = None


class CourseResponse(BaseModel):
    course_id: int
    course_name: str
    trainer: str
    duration: str


# ---------------- ENROLLMENT ----------------

class EnrollmentCreate(BaseModel):
    student_id: int
    course_id: int


class EnrollmentResponse(BaseModel):
    student_id: int
    course_id: int