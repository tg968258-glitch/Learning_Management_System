from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from Backend.database import get_db
from Backend.src.core.auth_dependency import get_current_user, require_roles
from Backend.src.models.assignment import Submission
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

@router.get("/", response_model=list[AssignmentResponse])
def list_assignments(
    course_id: int | None = Query(None, description="Filter by course ID"),
    module_id: int | None = Query(None, description="Filter by module ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    assignments = get_all_assignments(db, course_id=course_id, module_id=module_id)
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

    # Submissions visible: all for teachers/admins, only own for student
    if current_user.role == "student":
        student = db.query(Student).filter(Student.uid == current_user.uid).first()
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
        created = create_assignment(
            db=db,
            assignment_data=assignment_in.model_dump(),
            created_by_uid=current_user.uid
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
    student = db.query(Student).filter(Student.uid == current_user.uid).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )

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
    student = db.query(Student).filter(Student.uid == current_user.uid).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )

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

@router.put("/{assignment_id}/submissions/{student_id}/grade", response_model=SubmissionResponse)
def grade_student_submission(
    assignment_id: int,
    student_id: int,
    grade_in: SubmissionGrade,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher"))
):
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
        return _build_submission_response(db, submission)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e