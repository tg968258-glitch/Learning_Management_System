import random
import string

from fastapi.testclient import TestClient

from Backend.database import SessionLocal
from Backend.src.api_main import app
from Backend.src.core.security import create_access_token
from Backend.src.models.course import Course
from Backend.src.models.discussion import Discussion
from Backend.src.models.enrollment import Enrollment
from Backend.src.models.lesson import Lesson
from Backend.src.models.module import Module
from Backend.src.models.progress import LessonProgress
from Backend.src.models.student import Student
from Backend.src.models.user import User

client = TestClient(app)


def random_str(length=6):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def test_complete_live_lms_workflow():
    db = SessionLocal()
    suffix = random_str()

    print("\n=======================================================")
    print("       STARTING LIVE LMS INTEGRATION & DATABASE TEST")
    print("=======================================================")

    # 1. Setup Admin Account & Token
    admin_user = db.query(User).filter(User.role == "admin").first()
    if not admin_user:
        admin_uid = f"ADM{random_str(4)}"
        admin_user = User(
            uid=admin_uid,
            username=f"admin_{suffix}",
            email=f"admin_{suffix}@lms.com",
            role="admin",
            is_active=True,
            email_verified=True,
            password_hash="dummy_hash"
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

    admin_token = create_access_token(uid=admin_user.uid, role="admin")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print(f" [PASS] 1. AUTH: Admin configured -> Admin UID: {admin_user.uid}")

    # 2. Register a new Student User via /auth/register
    student_email = f"student_{suffix}@lms.com"
    student_username = f"std_{suffix}"
    student_password = "Password123"

    reg_payload = {
        "name": f"Student {suffix}",
        "username": student_username,
        "email": student_email,
        "password": student_password,
        "role": "student"
    }

    reg_res = client.post("/auth/register", json=reg_payload)
    assert reg_res.status_code == 200, f"Registration failed: {reg_res.text}"
    student_user_data = reg_res.json()
    student_uid = student_user_data["uid"]
    print(f" [PASS] 2. API: Registered Student User -> UID: {student_uid}, Email: {student_email}")

    # Verify Student User in PostgreSQL
    db_student_user = db.query(User).filter(User.uid == student_uid).first()
    assert db_student_user is not None, "Student user not saved in DB"
    assert db_student_user.role == "student"
    print(f" [PASS] 3. DB VERIFY: User table has UID '{student_uid}' with role 'student'")

    # 3. Verify & Update Student Profile via /students/{student_id} (Admin)
    created_student = db.query(Student).filter(Student.uid == student_uid).first()
    assert created_student is not None
    student_id = created_student.student_id

    student_profile_payload = {
        "gender": "female",
        "phone_number": "9876543210"
    }
    student_prof_res = client.put(f"/students/{student_id}", json=student_profile_payload, headers=admin_headers)
    assert student_prof_res.status_code == 200, f"Student profile update failed: {student_prof_res.text}"
    print(f" [PASS] 4. API & DB: Student Profile updated -> student_id: {student_id}")

    # 4. Login as Student via /auth/login
    login_res = client.post(
        "/auth/login",
        json={"email": student_email, "password": student_password}
    )
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    student_token = login_res.json()["access_token"]
    student_headers = {"Authorization": f"Bearer {student_token}"}
    print(" [PASS] 5. API: Student authenticated -> JWT Access Token obtained")

    # 5. Create a Course via /courses/ (Admin)
    course_name = f"Mastering FastAPI {suffix}"
    course_payload = {
        "course_name": course_name,
        "description": "Full end-to-end FastAPI course with PostgreSQL",
        "duration": "6 weeks",
        "status": "active",
        "category": "Backend Development"
    }
    course_res = client.post("/courses/", json=course_payload, headers=admin_headers)
    assert course_res.status_code == 201, f"Course creation failed: {course_res.text}"
    course_data = course_res.json()
    course_id = course_data["course_id"]
    print(f" [PASS] 6. API: Created Course -> ID: {course_id}, Name: '{course_name}'")

    # Verify Course in PostgreSQL
    db_course = db.query(Course).filter(Course.course_id == course_id).first()
    assert db_course is not None, "Course not found in DB"
    print(f" [PASS] 7. DB VERIFY: Course '{db_course.course_name}' stored in 'courses' table")

    # 6. Create Module & Lesson (Admin)
    module_payload = {
        "course_id": course_id,
        "module_name": "Module 1: Introduction",
        "order": 1
    }
    module_res = client.post("/modules/", json=module_payload, headers=admin_headers)
    assert module_res.status_code == 201, f"Module creation failed: {module_res.text}"
    module_id = module_res.json()["module_id"]
    print(f" [PASS] 8. API: Created Module -> ID: {module_id}")

    lesson_payload = {
        "module_id": module_id,
        "lesson_title": "Lesson 1: Installation & Routing",
        "order": 1,
        "duration_minutes": 30
    }
    lesson_res = client.post("/lessons/", json=lesson_payload, headers=admin_headers)
    assert lesson_res.status_code == 201, f"Lesson creation failed: {lesson_res.text}"
    lesson_id = lesson_res.json()["lesson_id"]
    print(f" [PASS] 9. API: Created Lesson -> ID: {lesson_id}")

    # 7. Student Enrolls in Course via /enrollments/
    enroll_payload = {
        "course_id": course_id
    }
    enroll_res = client.post("/enrollments/", json=enroll_payload, headers=student_headers)
    assert enroll_res.status_code in (200, 201), f"Enrollment failed: {enroll_res.text}"
    enroll_id = enroll_res.json()["enrollment_id"]
    print(f" [PASS] 10. API: Student Enrolled in Course -> Enrollment ID: {enroll_id}")

    # Verify Enrollment in PostgreSQL
    db_enrollment = db.query(Enrollment).filter(Enrollment.enrollment_id == enroll_id).first()
    assert db_enrollment is not None
    assert db_enrollment.status == "active"
    print(f" [PASS] 11. DB VERIFY: Active Enrollment found in 'enrollments' table (student_id={student_id}, course_id={course_id})")

    # 8. Student Updates Lesson Progress via /progress/
    progress_payload = {
        "progress_percentage": 100.0,
        "completed": True
    }
    progress_res = client.put(
        f"/progress/lesson/{lesson_id}",
        json=progress_payload,
        headers=student_headers
    )
    assert progress_res.status_code == 200, f"Progress update failed: {progress_res.text}"
    print(" [PASS] 12. API: Lesson Progress Updated to 100.0% (completed: True)")

    # Verify Progress in PostgreSQL
    db_progress = db.query(LessonProgress).filter(
        LessonProgress.student_id == student_id,
        LessonProgress.lesson_id == lesson_id
    ).first()
    assert db_progress is not None
    assert db_progress.completed is True
    print(f" [PASS] 13. DB VERIFY: Progress recorded in 'lesson_progress' table (completed: {db_progress.completed})")

    # 9. Post Discussion Message via /discussions/
    discussion_payload = {
        "course_id": course_id,
        "message": "Excited to join this FastAPI course!"
    }
    disc_res = client.post("/discussions/", json=discussion_payload, headers=student_headers)
    assert disc_res.status_code in (200, 201), f"Discussion failed: {disc_res.text}"
    disc_id = disc_res.json()["discussion_id"]
    print(f" [PASS] 14. API: Discussion Posted -> ID: {disc_id}")

    # Verify Discussion in PostgreSQL
    db_disc = db.query(Discussion).filter(Discussion.discussion_id == disc_id).first()
    assert db_disc is not None
    print(f" [PASS] 15. DB VERIFY: Discussion message '{db_disc.message}' found in 'discussions' table")

    # 10. Summary Verification of PostgreSQL Database Tables
    total_users = db.query(User).count()
    total_students = db.query(Student).count()
    total_courses = db.query(Course).count()
    total_modules = db.query(Module).count()
    total_lessons = db.query(Lesson).count()
    total_enrollments = db.query(Enrollment).count()
    total_progress = db.query(LessonProgress).count()
    total_discussions = db.query(Discussion).count()

    print("\n=======================================================")
    print("       POSTGRESQL DATABASE ROW COUNT SUMMARY")
    print("=======================================================")
    print(f"  • users:           {total_users} rows")
    print(f"  • students:        {total_students} rows")
    print(f"  • courses:         {total_courses} rows")
    print(f"  • modules:         {total_modules} rows")
    print(f"  • lessons:         {total_lessons} rows")
    print(f"  • enrollments:     {total_enrollments} rows")
    print(f"  • lesson_progress: {total_progress} rows")
    print(f"  • discussions:     {total_discussions} rows")
    print("=======================================================")
    print("  ALL LIVE TESTS & DB VERIFICATIONS PASSED 100%!")
    print("=======================================================\n")
    db.close()


if __name__ == "__main__":
    test_complete_live_lms_workflow()
