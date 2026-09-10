from pydantic import BaseModel


class AdminDashboardStats(BaseModel):
    total_courses: int
    total_students: int
    active_instructors: int
    active_enrollments: int


class TeacherDashboardStats(BaseModel):
    active_courses: int
    total_students: int
    assignments: int
    live_sessions: int


class StudentDashboardStats(BaseModel):
    enrolled_courses: int
    completed_lessons: int
    assignments: int
    upcoming_sessions: int
