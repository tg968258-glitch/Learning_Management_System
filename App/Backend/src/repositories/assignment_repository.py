from datetime import datetime
from sqlalchemy.orm import Session

from Backend.src.models.assignment import Assignment, Submission


class AssignmentRepository:
    # --- Assignment CRUD ---
    @staticmethod
    def get_by_id(db: Session, assignment_id: int) -> Assignment | None:
        return db.query(Assignment).filter(Assignment.assignment_id == assignment_id).first()

    @staticmethod
    def get_all(
        db: Session,
        course_id: int | None = None,
        module_id: int | None = None
    ) -> list[Assignment]:
        query = db.query(Assignment)
        if course_id:
            query = query.filter(Assignment.course_id == course_id)
        if module_id:
            query = query.filter(Assignment.module_id == module_id)
        return query.all()

    @staticmethod
    def create(db: Session, assignment_data: dict, created_by_uid: str) -> Assignment:
        assignment = Assignment(
            course_id=assignment_data["course_id"],
            module_id=assignment_data["module_id"],
            title=assignment_data["title"],
            description=assignment_data.get("description"),
            due_date=assignment_data["due_date"],
            max_marks=assignment_data["max_marks"],
            passing_marks=assignment_data["passing_marks"],
            created_by=created_by_uid,
            created_at=datetime.utcnow()
        )
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        return assignment

    @staticmethod
    def update(db: Session, assignment: Assignment, update_data: dict) -> Assignment:
        for field, value in update_data.items():
            if hasattr(assignment, field) and value is not None:
                setattr(assignment, field, value)
        assignment.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(assignment)
        return assignment

    @staticmethod
    def delete(db: Session, assignment: Assignment) -> None:
        db.query(Submission).filter(Submission.assignment_id == assignment.assignment_id).delete()
        db.delete(assignment)
        db.commit()

    # --- Submissions & Grading ---
    @staticmethod
    def get_submissions_by_assignment(db: Session, assignment_id: int) -> list[Submission]:
        return (
            db.query(Submission)
            .filter(Submission.assignment_id == assignment_id)
            .all()
        )

    @staticmethod
    def get_submission(db: Session, assignment_id: int, student_id: int) -> Submission | None:
        return (
            db.query(Submission)
            .filter(
                Submission.assignment_id == assignment_id,
                Submission.student_id == student_id
            )
            .first()
        )

    @staticmethod
    def create_or_update_submission(
        db: Session,
        assignment_id: int,
        student_id: int,
        submission_text: str | None,
        submission_file: str | None,
        status: str
    ) -> Submission:
        submission = AssignmentRepository.get_submission(db, assignment_id, student_id)
        now = datetime.utcnow()
        if submission:
            if submission_text is not None:
                submission.submission_text = submission_text
            if submission_file is not None:
                submission.submission_file = submission_file
            submission.submission_date = now
            submission.status = status
            submission.updated_at = now
        else:
            submission = Submission(
                assignment_id=assignment_id,
                student_id=student_id,
                submission_date=now,
                submission_text=submission_text,
                submission_file=submission_file,
                status=status,
                created_at=now
            )
            db.add(submission)

        db.commit()
        db.refresh(submission)
        return submission

    @staticmethod
    def grade_submission(
        db: Session,
        submission: Submission,
        marks: float,
        feedback: str | None,
        teacher_id: int | None
    ) -> Submission:
        submission.marks = marks
        submission.feedback = feedback
        submission.graded_by = teacher_id
        submission.status = "graded"
        submission.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(submission)
        return submission
