from sqlalchemy import func
from sqlalchemy.orm import Session

from Backend.src.models.assignment import Assignment, Submission
from Backend.src.models.course import Course
from Backend.src.models.enrollment import Enrollment
from Backend.src.models.quiz import Quiz, QuizAttempt
from Backend.src.models.student import Student
from Backend.src.models.teacher import Teacher
from Backend.src.models.user import User


class AdminRepository:
    @staticmethod
    def get_dashboard_stats(db: Session) -> dict:
        """Return only the aggregate values displayed by the admin dashboard."""
        row = db.query(
            db.query(func.count(Course.course_id)).scalar_subquery().label("total_courses"),
            db.query(func.count(Student.student_id)).scalar_subquery().label("total_students"),
            db.query(func.count(Teacher.teacher_id))
            .join(User, User.uid == Teacher.uid)
            .filter(User.is_active.is_(True))
            .scalar_subquery()
            .label("active_instructors"),
            db.query(func.count(Enrollment.enrollment_id))
            .filter(Enrollment.status == "active")
            .scalar_subquery()
            .label("active_enrollments"),
        ).one()
        return {key: int(value or 0) for key, value in row._mapping.items()}

    @staticmethod
    def get_dashboard_metrics(db: Session) -> dict:
        total_users = db.query(User).count()
        total_students = db.query(Student).count()
        total_teachers = db.query(Teacher).count()
        total_courses = db.query(Course).count()
        active_courses = db.query(Course).filter(Course.status == "active").count()
        total_enrollments = db.query(Enrollment).count()
        active_enrollments = db.query(Enrollment).filter(Enrollment.status == "active").count()
        total_assignments = db.query(Assignment).count()
        total_submissions = db.query(Submission).count()
        total_quizzes = db.query(Quiz).count()
        total_quiz_attempts = db.query(QuizAttempt).count()

        return {
            "total_users": total_users,
            "total_students": total_students,
            "total_teachers": total_teachers,
            "total_courses": total_courses,
            "active_courses": active_courses,
            "total_enrollments": total_enrollments,
            "active_enrollments": active_enrollments,
            "total_assignments": total_assignments,
            "total_submissions": total_submissions,
            "total_quizzes": total_quizzes,
            "total_quiz_attempts": total_quiz_attempts
        }
