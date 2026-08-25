from Backend.src.models.announcement import Announcement
from Backend.src.models.assignment import Assignment, Submission
from Backend.src.models.audit_log import AuditLog
from Backend.src.models.class_session import ClassSession
from Backend.src.models.course import Course, CourseTeacher
from Backend.src.models.discussion import Discussion
from Backend.src.models.enrollment import Enrollment
from Backend.src.models.lesson import Lesson, LessonContent, Resource
from Backend.src.models.module import Module
from Backend.src.models.notification import Notification
from Backend.src.models.progress import LessonProgress
from Backend.src.models.quiz import (
    QuestionOption,
    Quiz,
    QuizAttempt,
    QuizQuestion,
    StudentAnswer,
)
from Backend.src.models.student import Student
from Backend.src.models.teacher import Teacher
from Backend.src.models.teacher_invitation import TeacherInvitation
from Backend.src.models.user import OTPVerification, User, UserSession
