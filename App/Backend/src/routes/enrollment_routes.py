from fastapi import APIRouter, Depends, HTTPException, Query, status
from math import ceil
from sqlalchemy import String, cast, or_
from sqlalchemy.orm import Session

from Backend.database import get_db
from Backend.src.core.auth_dependency import get_current_user, require_roles
from Backend.src.core.course_access import accessible_course_ids, require_course_access
from Backend.src.models.course import Course
from Backend.src.models.enrollment import Enrollment
from Backend.src.models.student import Student
from Backend.src.models.user import User
from Backend.src.schemas.enrollments import (
    EnrollmentCreate,
    EnrollmentResponse,
)
from Backend.src.services.enrollment_service import (
    create_enrollment,
    delete_enrollment,
    get_all_enrollments,
    get_course_enrollments,
    get_enrollment,
    get_student_enrollments,
)
from Backend.src.services.notification_service import create_notification

router = APIRouter(
    prefix="/enrollments",
    tags=["Enrollments"]
)


def _build_enrollment_response(db: Session, enrollment: Enrollment) -> dict:
    student = db.query(Student).filter(Student.student_id == enrollment.student_id).first()
    user = db.query(User).filter(User.uid == student.uid).first() if student else None
    course = db.query(Course).filter(Course.course_id == enrollment.course_id).first()

    return {
        "enrollment_id": enrollment.enrollment_id,
        "student_id": enrollment.student_id,
        "course_id": enrollment.course_id,
        "enrollment_date": enrollment.enrollment_date,
        "status": enrollment.status,
        "student_name": student.name if student else None,
        "student_uid": student.uid if student else None,
        "student_email": user.email if user else None,
        "course_name": course.course_name if course else None,
    }


# =========================================================
# LIST ALL ENROLLMENTS (Admin, Teacher)
# =========================================================

@router.get("/page")
def paginated_enrollments(
    page: int = Query(1, ge=1),
    page_size: int = Query(6, ge=1, le=100),
    search: str | None = Query(None, max_length=150),
    status_filter: str | None = Query(None, alias="status"),
    course_id: int | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher")),
):
    query = db.query(Enrollment).join(Student, Student.student_id == Enrollment.student_id).join(
        User, User.uid == Student.uid
    ).join(Course, Course.course_id == Enrollment.course_id)
    allowed = accessible_course_ids(db, current_user)
    if allowed is not None:
        query = query.filter(Enrollment.course_id.in_(allowed))
    if status_filter:
        query = query.filter(Enrollment.status == status_filter)
    if course_id is not None:
        query = query.filter(Enrollment.course_id == course_id)
    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(or_(
            Student.name.ilike(term), User.email.ilike(term), Student.uid.ilike(term),
            Course.course_name.ilike(term), cast(Student.student_id, String).ilike(term),
            cast(Course.course_id, String).ilike(term),
        ))
    total = query.count()
    rows = query.order_by(Enrollment.enrollment_date.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "items": [_build_enrollment_response(db, row) for row in rows],
        "page": page, "page_size": page_size, "total": total,
        "total_pages": ceil(total / page_size) if total else 0,
    }

@router.get("/", response_model=list[EnrollmentResponse])
def list_enrollments(
    status: str | None = Query(None, description="Filter by status (e.g. active, pending)"),
    course_id: int | None = Query(None, description="Filter by course ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher"))
):
    enrollments = get_all_enrollments(db, status=status)
    allowed_course_ids = accessible_course_ids(db, current_user)
    if allowed_course_ids is not None:
        enrollments = [e for e in enrollments if e.course_id in allowed_course_ids]
    if course_id is not None:
        if course_id <= 0:
            raise HTTPException(status_code=400, detail="Course ID must be positive")
        require_course_access(db, current_user, course_id)
        enrollments = [e for e in enrollments if e.course_id == course_id]
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

    require_course_access(db, current_user, course_id)

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
# SELF-ENROLL CURRENT STUDENT
# =========================================================

@router.post("/", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
def add_new_enrollment(
    enrollment_in: EnrollmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("student"))
):
    student = db.query(Student).filter(Student.uid == current_user.uid).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found. Please complete your profile first."
        )

    try:
        created = create_enrollment(
            db=db,
            student_id=student.student_id,
            course_id=enrollment_in.course_id,
            status="active"
        )
        course = db.query(Course).filter(Course.course_id == enrollment_in.course_id).first()
        create_notification(db, {
            "uid": student.uid,
            "notification_type": "enrollment",
            "title": "Course enrollment confirmed",
            "message": f"You are now enrolled in {course.course_name if course else 'the course'}.",
        })
        return _build_enrollment_response(db, created)
    except ValueError as e:
        error_status = status.HTTP_409_CONFLICT if "already enrolled" in str(e).lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(
            status_code=error_status,
            detail=str(e)
        ) from e


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
