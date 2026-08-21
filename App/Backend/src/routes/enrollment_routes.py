from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from Backend.database import get_db
from Backend.src.core.auth_dependency import get_current_user, require_roles
from Backend.src.models.course import Course
from Backend.src.models.enrollment import Enrollment
from Backend.src.models.student import Student
from Backend.src.models.user import User
from Backend.src.schemas.enrollments import (
    EnrollmentCreate,
    EnrollmentResponse,
    EnrollmentStatusUpdate,
)
from Backend.src.services.enrollment_service import (
    create_enrollment,
    delete_enrollment,
    get_all_enrollments,
    get_course_enrollments,
    get_enrollment,
    get_student_enrollments,
    update_enrollment_status,
)

router = APIRouter(
    prefix="/enrollments",
    tags=["Enrollments"]
)


def _build_enrollment_response(db: Session, enrollment: Enrollment) -> dict:
    student = db.query(Student).filter(Student.student_id == enrollment.student_id).first()
    course = db.query(Course).filter(Course.course_id == enrollment.course_id).first()

    return {
        "enrollment_id": enrollment.enrollment_id,
        "student_id": enrollment.student_id,
        "course_id": enrollment.course_id,
        "enrollment_date": enrollment.enrollment_date,
        "status": enrollment.status,
        "student_name": student.name if student else None,
        "course_name": course.course_name if course else None,
    }


# =========================================================
# LIST ALL ENROLLMENTS (Admin, Teacher)
# =========================================================

@router.get("/", response_model=list[EnrollmentResponse])
def list_enrollments(
    status: str | None = Query(None, description="Filter by status (e.g. active, pending)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher"))
):
    enrollments = get_all_enrollments(db, status=status)
    return [_build_enrollment_response(db, e) for e in enrollments]


# =========================================================
# GET CURRENT STUDENT'S ENROLLMENTS
# =========================================================

@router.get("/my-enrollments", response_model=list[EnrollmentResponse])
def get_my_enrollments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("student"))
):
    student = db.query(Student).filter(Student.uid == current_user.uid).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found for this user"
        )

    enrollments = get_student_enrollments(db, student.student_id)
    return [_build_enrollment_response(db, e) for e in enrollments]


# =========================================================
# GET ENROLLMENTS BY COURSE (Admin, Teacher)
# =========================================================

@router.get("/course/{course_id}", response_model=list[EnrollmentResponse])
def get_enrollments_for_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher"))
):
    if course_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course ID must be positive"
        )

    enrollments = get_course_enrollments(db, course_id)
    return [_build_enrollment_response(db, e) for e in enrollments]


# =========================================================
# GET SINGLE ENROLLMENT
# =========================================================

@router.get("/{enrollment_id}", response_model=EnrollmentResponse)
def get_single_enrollment(
    enrollment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if enrollment_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Enrollment ID must be positive"
        )

    enrollment = get_enrollment(db, enrollment_id)
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found"
        )

    # If student, verify it is their enrollment
    if current_user.role == "student":
        student = db.query(Student).filter(Student.uid == current_user.uid).first()
        if not student or enrollment.student_id != student.student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to view this enrollment"
            )

    return _build_enrollment_response(db, enrollment)


# =========================================================
# CREATE ENROLLMENT
# =========================================================

@router.post("/", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
def add_new_enrollment(
    enrollment_in: EnrollmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Determine student_id
    if current_user.role == "student":
        student = db.query(Student).filter(Student.uid == current_user.uid).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student profile not found. Please complete your profile first."
            )
        target_student_id = student.student_id
    else:
        # Admin or Teacher enrolling a student
        if not enrollment_in.student_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="student_id is required when enrolling as admin/teacher"
            )
        target_student_id = enrollment_in.student_id

    try:
        created = create_enrollment(
            db=db,
            student_id=target_student_id,
            course_id=enrollment_in.course_id,
            status="active"
        )
        return _build_enrollment_response(db, created)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e


# =========================================================
# UPDATE ENROLLMENT STATUS (Admin, Teacher)
# =========================================================

@router.put("/{enrollment_id}/status", response_model=EnrollmentResponse)
def change_enrollment_status(
    enrollment_id: int,
    status_update: EnrollmentStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher"))
):
    if enrollment_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Enrollment ID must be positive"
        )

    updated = update_enrollment_status(
        db=db,
        enrollment_id=enrollment_id,
        new_status=status_update.status
    )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found"
        )

    return _build_enrollment_response(db, updated)


# =========================================================
# DELETE ENROLLMENT (Admin only)
# =========================================================

@router.delete("/{enrollment_id}")
def remove_enrollment(
    enrollment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    if enrollment_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Enrollment ID must be positive"
        )

    deleted = delete_enrollment(db, enrollment_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found"
        )

    return {"message": "Enrollment deleted successfully"}