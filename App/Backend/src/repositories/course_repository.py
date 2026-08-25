from datetime import datetime
from sqlalchemy.orm import Session

from Backend.src.models.course import Course, CourseTeacher
from Backend.src.models.teacher import Teacher


class CourseRepository:
    @staticmethod
    def get_by_id(db: Session, course_id: int) -> Course | None:
        return db.query(Course).filter(Course.course_id == course_id).first()

    @staticmethod
    def get_all(
        db: Session,
        status: str | None = None,
        category: str | None = None
    ) -> list[Course]:
        query = db.query(Course)
        if status:
            query = query.filter(Course.status == status)
        if category:
            query = query.filter(Course.category == category)
        return query.all()

    @staticmethod
    def count(db: Session, status: str | None = None) -> int:
        query = db.query(Course)
        if status:
            query = query.filter(Course.status == status)
        return query.count()

    @staticmethod
    def create(db: Session, course_data: dict, created_by_uid: str | None = None) -> Course:
        course = Course(
            course_name=course_data["course_name"],
            description=course_data.get("description"),
            duration=course_data.get("duration"),
            status=course_data.get("status", "draft"),
            category=course_data.get("category"),
            created_by=created_by_uid,
            created_at=datetime.utcnow()
        )
        db.add(course)
        db.commit()
        db.refresh(course)
        return course

    @staticmethod
    def update(db: Session, course: Course, update_data: dict) -> Course:
        for field, value in update_data.items():
            if hasattr(course, field) and value is not None:
                setattr(course, field, value)
        course.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(course)
        return course

    @staticmethod
    def delete(db: Session, course: Course) -> None:
        # Clear teacher associations
        db.query(CourseTeacher).filter(CourseTeacher.course_id == course.course_id).delete()
        db.delete(course)
        db.commit()

    @staticmethod
    def get_teachers_by_course(db: Session, course_id: int) -> list[Teacher]:
        return (
            db.query(Teacher)
            .join(CourseTeacher, CourseTeacher.teacher_id == Teacher.teacher_id)
            .filter(CourseTeacher.course_id == course_id)
            .all()
        )

    @staticmethod
    def get_courses_by_teacher(db: Session, teacher_id: int) -> list[Course]:
        return (
            db.query(Course)
            .join(CourseTeacher, CourseTeacher.course_id == Course.course_id)
            .filter(CourseTeacher.teacher_id == teacher_id)
            .all()
        )

    @staticmethod
    def set_course_teachers(db: Session, course_id: int, teacher_ids: list[int]) -> list[Teacher]:
        db.query(CourseTeacher).filter(CourseTeacher.course_id == course_id).delete()
        assigned_teachers = []
        for teacher_id in set(teacher_ids):
            teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
            if not teacher:
                raise ValueError(f"Teacher with ID {teacher_id} not found")
            db.add(CourseTeacher(course_id=course_id, teacher_id=teacher_id))
            assigned_teachers.append(teacher)
        db.commit()
        return assigned_teachers
