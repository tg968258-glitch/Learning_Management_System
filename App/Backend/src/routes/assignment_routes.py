from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from math import ceil
from sqlalchemy import String, cast, or_
from sqlalchemy.orm import Session

from Backend.database import get_db
from Backend.src.core.auth_dependency import get_current_user, require_roles
from Backend.src.core.course_access import accessible_course_ids, require_course_access
from Backend.src.models.assignment import Assignment, Submission
from Backend.src.models.course import Course
from Backend.src.models.enrollment import Enrollment
from Backend.src.models.student import Student
from Backend.src.models.teacher import Teacher
from Backend.src.models.user import User
from Backend.src.utils.file_upload import save_uploaded_file
from Backend.src.schemas.assignments import (
    AssignmentCreate,
    AssignmentDetailResponse,
    AssignmentResponse,
    AssignmentUpdate,
    SubmissionCreate,
    SubmissionGrade,
    SubmissionResponse,
)
from Backend.src.services.assignment_service import (
    create_assignment,
    delete_assignment,
    get_all_assignments,
    get_assignment_by_id,
    get_assignment_submissions,
    get_submission,
    grade_submission,
    submit_assignment,
    update_assignment,
)

router = APIRouter(
    prefix="/assignments",
    tags=["Assignments"]
)
from Backend.src.services.notification_service import create_notification, notify_course_students


def _get_student(db: Session, current_user: User) -> Student:
    student = db.query(Student).filter(Student.uid == current_user.uid).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    return student


def _require_student_course_access(db: Session, current_user: User, course_id: int):
    if current_user.role != "student":
        return None
    student = _get_student(db, current_user)
    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == student.student_id,
        Enrollment.course_id == course_id,
        Enrollment.status == "active"
    ).first()
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be actively enrolled in this course to access its assignments"
        )
    return student


def _build_submission_response(db: Session, sub: Submission) -> dict:
    student = db.query(Student).filter(Student.student_id == sub.student_id).first()
    return {
        "submission_id": sub.submission_id,
        "assignment_id": sub.assignment_id,
        "student_id": sub.student_id,
        "submission_date": sub.submission_date,
        "submission_text": sub.submission_text,
        "submission_file": sub.submission_file,
        "status": sub.status,
        "marks": float(sub.marks) if sub.marks is not None else None,
        "graded_by": sub.graded_by,
        "feedback": sub.feedback,
        "student_name": student.name if student else None
    }


# =========================================================
# LIST ASSIGNMENTS
# =========================================================

@router.get("/page")
def paginated_assignments(
    page: int = Query(1, ge=1),
    page_size: int = Query(6, ge=1, le=100),
    search: str | None = Query(None, max_length=150),
    course_id: int | None = Query(None),
    module_id: int | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Assignment).join(Course, Course.course_id == Assignment.course_id)
    allowed = accessible_course_ids(db, current_user)
    if allowed is not None:
        query = query.filter(Assignment.course_id.in_(allowed))
    if course_id is not None:
        query = query.filter(Assignment.course_id == course_id)
    if module_id is not None:
        query = query.filter(Assignment.module_id == module_id)
    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(or_(
            Assignment.title.ilike(term),
            Assignment.description.ilike(term),
            Course.course_name.ilike(term),
            cast(Assignment.course_id, String).ilike(term),
        ))
    total = query.count()
    rows = query.order_by(Assignment.due_date.desc()).offset((page - 1) * page_size).limit(page_size).all()
    items = [{
        "assignment_id": a.assignment_id, "course_id": a.course_id, "module_id": a.module_id,
        "title": a.title, "description": a.description, "due_date": a.due_date,
        "max_marks": float(a.max_marks), "passing_marks": float(a.passing_marks),
        "created_by": a.created_by, "created_at": a.created_at, "updated_at": a.updated_at,
        "course_name": db.query(Course.course_name).filter(Course.course_id == a.course_id).scalar(),
    } for a in rows]
    return {"items": items, "page": page, "page_size": page_size, "total": total, "total_pages": ceil(total / page_size) if total else 0}

@router.get("/", response_model=list[AssignmentResponse])
def list_assignments(
    course_id: int | None = Query(None, description="Filter by course ID"),
    module_id: int | None = Query(None, description="Filter by module ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    assignments = get_all_assignments(db, course_id=course_id, module_id=module_id)
    allowed_course_ids = accessible_course_ids(db, current_user)
    if allowed_course_ids is not None:
        assignments = [a for a in assignments if a.course_id in allowed_course_ids]
    return [
        {
            "assignment_id": a.assignment_id,
            "course_id": a.course_id,
            "module_id": a.module_id,
            "title": a.title,
            "description": a.description,
            "due_date": a.due_date,
            "max_marks": float(a.max_marks),
            "passing_marks": float(a.passing_marks),
            "created_by": a.created_by,
            "created_at": a.created_at,
            "updated_at": a.updated_at
        }
        for a in assignments
    ]


# =========================================================
# GET SINGLE ASSIGNMENT
# =========================================================

@router.get("/{assignment_id}", response_model=AssignmentDetailResponse)
def get_single_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if assignment_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assignment ID must be positive"
        )

    assignment = get_assignment_by_id(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )

    require_course_access(db, current_user, assignment.course_id)
    student = _get_student(db, current_user) if current_user.role == "student" else None

    # Submissions visible: all for teachers/admins, only own for student
    if current_user.role == "student":
        if student:
            sub = get_submission(db, assignment_id, student.student_id)
            submissions = [_build_submission_response(db, sub)] if sub else []
        else:
            submissions = []
    else:
        subs = get_assignment_submissions(db, assignment_id)
        submissions = [_build_submission_response(db, s) for s in subs]

    return {
        "assignment_id": assignment.assignment_id,
        "course_id": assignment.course_id,
        "module_id": assignment.module_id,
        "title": assignment.title,
        "description": assignment.description,
        "due_date": assignment.due_date,
        "max_marks": float(assignment.max_marks),
        "passing_marks": float(assignment.passing_marks),
        "created_by": assignment.created_by,
        "created_at": assignment.created_at,
        "updated_at": assignment.updated_at,
        "submissions": submissions
    }


def _notify_student_graded(db: Session, submission: Submission) -> None:
    student = db.query(Student).filter(Student.student_id == submission.student_id).first()
    assignment = get_assignment_by_id(db, submission.assignment_id)
    if student:
        create_notification(db, {
            "uid": student.uid,
            "assignment_id": submission.assignment_id,
            "notification_type": "grade",
            "title": "Assignment graded",
            "message": f"Your submission for {assignment.title if assignment else 'an assignment'} has been graded.",
        })


@router.get("/{assignment_id}/submissions", response_model=list[SubmissionResponse])
def list_assignment_submissions(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher"))
):
    assignment = get_assignment_by_id(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )

    require_course_access(db, current_user, assignment.course_id)

    submissions = get_assignment_submissions(db, assignment_id)
    return [_build_submission_response(db, submission) for submission in submissions]


@router.get("/{assignment_id}/my-submission", response_model=SubmissionResponse)
def get_my_assignment_submission(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("student"))
):
    """Return only the current student's submission for an assignment."""
    assignment = get_assignment_by_id(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    student = _require_student_course_access(db, current_user, assignment.course_id)

    submission = get_submission(db, assignment_id, student.student_id)
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No submission found for this assignment"
        )
    return _build_submission_response(db, submission)


# =========================================================
# CREATE ASSIGNMENT (Admin or Teacher)
# =========================================================

@router.post("/", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
def add_new_assignment(
    assignment_in: AssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher"))
):
    try:
        require_course_access(db, current_user, assignment_in.course_id)
        created = create_assignment(
            db=db,
            assignment_data=assignment_in.model_dump(),
            created_by_uid=current_user.uid
        )
        notify_course_students(
            db, created.course_id, "assignment", "New assignment",
            f"{created.title} has been added to your course.",
            assignment_id=created.assignment_id,
        )
        return {
            "assignment_id": created.assignment_id,
            "course_id": created.course_id,
            "module_id": created.module_id,
            "title": created.title,
            "description": created.description,
            "due_date": created.due_date,
            "max_marks": float(created.max_marks),
            "passing_marks": float(created.passing_marks),
            "created_by": created.created_by,
            "created_at": created.created_at,
            "updated_at": created.updated_at
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e


# =========================================================
# UPDATE ASSIGNMENT (Admin or Teacher)
# =========================================================

@router.put("/{assignment_id}", response_model=AssignmentResponse)
def update_existing_assignment(
    assignment_id: int,
    assignment_in: AssignmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher"))
):
    if assignment_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assignment ID must be positive"
        )

    existing = get_assignment_by_id(db, assignment_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Assignment not found")
    require_course_access(db, current_user, existing.course_id)

    try:
        updated = update_assignment(
            db=db,
            assignment_id=assignment_id,
            updated_data=assignment_in.model_dump(exclude_unset=True)
        )
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found"
            )

        return {
            "assignment_id": updated.assignment_id,
            "course_id": updated.course_id,
            "module_id": updated.module_id,
            "title": updated.title,
            "description": updated.description,
            "due_date": updated.due_date,
            "max_marks": float(updated.max_marks),
            "passing_marks": float(updated.passing_marks),
            "created_by": updated.created_by,
            "created_at": updated.created_at,
            "updated_at": updated.updated_at
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e


# =========================================================
# DELETE ASSIGNMENT (Admin or Teacher)
# =========================================================

@router.delete("/{assignment_id}")
def remove_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher"))
):
    if assignment_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assignment ID must be positive"
        )

    existing = get_assignment_by_id(db, assignment_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Assignment not found")
    require_course_access(db, current_user, existing.course_id)

    deleted = delete_assignment(db, assignment_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )

    return {"message": "Assignment deleted successfully"}


# =========================================================
# SUBMIT ASSIGNMENT (Student only)
# =========================================================

@router.post("/{assignment_id}/submit", response_model=SubmissionResponse)
def submit_work(
    assignment_id: int,
    submission_in: SubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("student"))
):
    assignment = get_assignment_by_id(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    student = _require_student_course_access(db, current_user, assignment.course_id)

    try:
        submission = submit_assignment(
            db=db,
            assignment_id=assignment_id,
            student_id=student.student_id,
            submission_data=submission_in.model_dump()
        )
        return _build_submission_response(db, submission)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e


# =========================================================
# SUBMIT ASSIGNMENT WITH FILE UPLOAD (PDF / TEXT)
# =========================================================

@router.post("/{assignment_id}/submit-file", response_model=SubmissionResponse)
async def submit_assignment_with_file(
    assignment_id: int,
    submission_text: str | None = Form(None),
    file: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("student"))
):
    assignment = get_assignment_by_id(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    student = _require_student_course_access(db, current_user, assignment.course_id)

    file_url = None
    if file and file.filename:
        file_url = await save_uploaded_file(file, subfolder="assignments")

    if not submission_text and not file_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide submission text or upload a PDF/document file"
        )

    try:
        submission = submit_assignment(
            db=db,
            assignment_id=assignment_id,
            student_id=student.student_id,
            submission_data={
                "submission_text": submission_text,
                "submission_file": file_url
            }
        )
        return _build_submission_response(db, submission)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e


# =========================================================
# GRADE SUBMISSION (Teacher or Admin)
# =========================================================

@router.post("/submissions/{submission_id}/grade", response_model=SubmissionResponse)
def grade_submission_by_id(
    submission_id: int,
    grade_in: SubmissionGrade,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher"))
):
    submission = db.query(Submission).filter(Submission.submission_id == submission_id).first()
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )

    assignment = get_assignment_by_id(db, submission.assignment_id)
    if assignment:
        require_course_access(db, current_user, assignment.course_id)

    teacher_id = None
    if current_user.role == "teacher":
        teacher = db.query(Teacher).filter(Teacher.uid == current_user.uid).first()
        teacher_id = teacher.teacher_id if teacher else None

    try:
        graded = grade_submission(
            db=db,
            assignment_id=submission.assignment_id,
            student_id=submission.student_id,
            marks=grade_in.marks,
            feedback=grade_in.feedback,
            teacher_id=teacher_id
        )
        _notify_student_graded(db, graded)
        return _build_submission_response(db, graded)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e

@router.put("/{assignment_id}/submissions/{student_id}/grade", response_model=SubmissionResponse)
def grade_student_submission(
    assignment_id: int,
    student_id: int,
    grade_in: SubmissionGrade,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher"))
):
    assignment = get_assignment_by_id(db, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    require_course_access(db, current_user, assignment.course_id)

    # Find teacher_id if user is a teacher
    teacher_id = None
    if current_user.role == "teacher":
        teacher = db.query(Teacher).filter(Teacher.uid == current_user.uid).first()
        if teacher:
            teacher_id = teacher.teacher_id

    try:
        submission = grade_submission(
            db=db,
            assignment_id=assignment_id,
            student_id=student_id,
            marks=grade_in.marks,
            feedback=grade_in.feedback,
            teacher_id=teacher_id
        )
        _notify_student_graded(db, submission)
        return _build_submission_response(db, submission)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e
