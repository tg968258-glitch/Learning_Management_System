"""
seed_db.py
Comprehensive database seeding script for LMS (FastAPI & Spring Boot).
Populates realistic linked data across all 26 tables.
Uses Argon2id password hashing compatible with both FastAPI (pwdlib) and Spring Boot (Argon2PasswordEncoder).
"""

import datetime
from decimal import Decimal
from pathlib import Path
from sqlalchemy import text
from Backend.database import SessionLocal, engine
from Backend.src.core.security import hash_password

BASE_DIR = Path(__file__).resolve().parent

def seed_database():
    db = SessionLocal()
    try:
        print("--- Clearing existing data ---")
        tables_to_clear = [
            "student_answers",
            "quiz_attempts",
            "question_options",
            "quiz_questions",
            "quizzes",
            "submissions",
            "assignments",
            "lesson_progress",
            "resources",
            "lesson_contents",
            "lessons",
            "modules",
            "enrollments",
            "course_teachers",
            "discussions",
            "announcements",
            "notifications",
            "class_sessions",
            "courses",
            "teacher_invitations",
            "students",
            "teachers",
            "user_sessions",
            "otp_verifications",
            "audit_logs",
            "users",
        ]
        for t in tables_to_clear:
            db.execute(text(f"TRUNCATE TABLE {t} RESTART IDENTITY CASCADE;"))
        db.commit()
        print("All tables cleared successfully.")

        print("--- Seeding Users ---")
        # Shared password hashes
        admin_hash = hash_password("admin123")
        teacher_hash = hash_password("teacher123")
        student_hash = hash_password("student123")

        users_data = [
            # Admin
            ("USR001", "admin", "admin@lms.com", None, admin_hash, "admin", True, False, True),
            # Teachers
            ("USR002", "riyasharma", "riya@example.com", "riya.rec@gmail.com", teacher_hash, "teacher", True, False, True),
            ("USR003", "vikrampatel", "vikram@example.com", "vikram.rec@gmail.com", teacher_hash, "teacher", True, False, True),
            ("USR004", "nehadixit", "neha@example.com", None, teacher_hash, "teacher", True, False, True),
            # Students
            ("USR005", "aaravjain", "aarav@example.com", None, student_hash, "student", True, False, True),
            ("USR006", "ananyasharma", "ananya@example.com", None, student_hash, "student", True, False, True),
            ("USR007", "rohitverma", "rohit@example.com", None, student_hash, "student", True, False, True),
            ("USR008", "priyasingh", "priya@example.com", None, student_hash, "student", True, False, True),
            ("USR009", "kabirmehta", "kabir@example.com", None, student_hash, "student", True, False, True),
        ]

        for u in users_data:
            db.execute(text("""
                INSERT INTO users (uid, username, email, recovery_email, password_hash, role, email_verified, recovery_email_verified, is_active)
                VALUES (:uid, :username, :email, :rec, :pw, :role, :ev, :rev, :ia)
            """), {"uid": u[0], "username": u[1], "email": u[2], "rec": u[3], "pw": u[4], "role": u[5], "ev": u[6], "rev": u[7], "ia": u[8]})

        print("--- Seeding Teachers & Students Profiles ---")
        teachers_data = [
            ("USR002", "Prof. Riya Sharma", "9876543210", "FastAPI & Python Architecture", "Ph.D. in Computer Science", 8),
            ("USR003", "Dr. Vikram Patel", "9876543211", "Java & Spring Cloud Systems", "M.Tech in Software Engineering", 10),
            ("USR004", "Neha Dixit", "9876543212", "React & Modern Web Development", "M.S. in Computer Science", 5),
        ]
        for t in teachers_data:
            db.execute(text("""
                INSERT INTO teachers (uid, name, phone_number, specialization, qualification, experience)
                VALUES (:uid, :name, :phone, :spec, :qual, :exp)
            """), {"uid": t[0], "name": t[1], "phone": t[2], "spec": t[3], "qual": t[4], "exp": t[5]})

        students_data = [
            ("USR005", "Aarav Jain", "2003-05-14", "Male", "9123456780"),
            ("USR006", "Ananya Sharma", "2002-11-20", "Female", "9123456781"),
            ("USR007", "Rohit Verma", "2003-02-18", "Male", "9123456782"),
            ("USR008", "Priya Singh", "2004-08-09", "Female", "9123456783"),
            ("USR009", "Kabir Mehta", "2003-09-25", "Male", "9123456784"),
        ]
        for s in students_data:
            db.execute(text("""
                INSERT INTO students (uid, name, date_of_birth, gender, phone_number)
                VALUES (:uid, :name, :dob, :gender, :phone)
            """), {"uid": s[0], "name": s[1], "dob": s[2], "gender": s[3], "phone": s[4]})

        print("--- Seeding Courses ---")
        courses_data = [
            ("Mastering FastAPI & Cloud Architecture", "Comprehensive backend engineering covering async routing, Pydantic v2, dependency injection, SQLAlchemy, and Redis caching.", "8 weeks", "active", "Backend Development", "USR001", "USR001"),
            ("Enterprise Java & Spring Boot 3", "Production-grade microservices with Spring Boot, Spring Security, Flyway, PostgreSQL, and Docker containerization.", "10 weeks", "active", "Backend Development", "USR001", "USR001"),
            ("Modern Full-Stack React & Next.js", "Hands-on web development with Next.js App Router, TypeScript, TailwindCSS, and state management.", "6 weeks", "active", "Frontend Development", "USR001", "USR001"),
            ("High-Performance Database Systems", "Advanced SQL, indexing strategies, query execution plans, and caching with Valkey / Redis.", "4 weeks", "draft", "Database", "USR001", None),
        ]
        for c in courses_data:
            db.execute(text("""
                INSERT INTO courses (course_name, description, duration, status, category, created_by, published_by, created_at)
                VALUES (:name, :desc, :dur, :status, :cat, :cb, :pb, NOW())
            """), {"name": c[0], "desc": c[1], "dur": c[2], "status": c[3], "cat": c[4], "cb": c[5], "pb": c[6]})

        print("--- Seeding Course Teachers & Enrollments ---")
        # Course 1 (FastAPI) -> Teacher 1 (Riya, teacher_id=1)
        # Course 2 (Spring Boot) -> Teacher 2 (Vikram, teacher_id=2)
        # Course 3 (Next.js) -> Teacher 3 (Neha, teacher_id=3)
        db.execute(text("INSERT INTO course_teachers (course_id, teacher_id, is_course_admin) VALUES (1, 1, true)"))
        db.execute(text("INSERT INTO course_teachers (course_id, teacher_id, is_course_admin) VALUES (2, 2, true)"))
        db.execute(text("INSERT INTO course_teachers (course_id, teacher_id, is_course_admin) VALUES (3, 3, true)"))

        # Enrollments for students (student_id 1 to 5)
        db.execute(text("INSERT INTO enrollments (student_id, course_id, enrollment_date, status) VALUES (1, 1, '2026-09-01', 'active')"))
        db.execute(text("INSERT INTO enrollments (student_id, course_id, enrollment_date, status) VALUES (1, 2, '2026-09-01', 'active')"))
        db.execute(text("INSERT INTO enrollments (student_id, course_id, enrollment_date, status) VALUES (2, 1, '2026-09-02', 'active')"))
        db.execute(text("INSERT INTO enrollments (student_id, course_id, enrollment_date, status) VALUES (2, 3, '2026-09-02', 'active')"))
        db.execute(text("INSERT INTO enrollments (student_id, course_id, enrollment_date, status) VALUES (3, 2, '2026-09-03', 'active')"))
        db.execute(text("INSERT INTO enrollments (student_id, course_id, enrollment_date, status) VALUES (4, 1, '2026-09-03', 'active')"))
        db.execute(text("INSERT INTO enrollments (student_id, course_id, enrollment_date, status) VALUES (5, 3, '2026-09-04', 'active')"))

        print("--- Seeding Modules & Lessons ---")
        modules_data = [
            # Course 1 modules
            (1, True, "USR001", "Getting Started & Core Concepts", "Introduction to FastAPI async ecosystem, ASGI, and dependency injection."),
            (1, True, "USR001", "Database Integration & Caching", "Connecting PostgreSQL with SQLAlchemy 2.0 and Valkey/Redis caching."),
            (1, True, "USR001", "Authentication & Security", "JWT authentication, password hashing, and role-based access control."),
            # Course 2 modules
            (2, True, "USR001", "Spring Boot 3 Core Architecture", "Dependency injection, configuration properties, and REST controllers."),
            (2, True, "USR001", "Spring Data JPA & Security", "JPA entities, Flyway migrations, and Spring Security 6 stateless JWT."),
        ]
        for m in modules_data:
            db.execute(text("""
                INSERT INTO modules (course_id, is_published, published_by, module_name, description)
                VALUES (:cid, :pub, :pb, :name, :desc)
            """), {"cid": m[0], "pub": m[1], "pb": m[2], "name": m[3], "desc": m[4]})

        lessons_data = [
            # Module 1 lessons
            (1, True, "FastAPI Application Structure & Routing"),
            (1, True, "Request Validation with Pydantic v2"),
            (1, True, "Dependency Injection & Middleware"),
            # Module 2 lessons
            (2, True, "SQLAlchemy 2.0 Engine and Session Setup"),
            (2, True, "Valkey / Redis Integration & Cache Invalidation"),
            # Module 3 lessons
            (3, True, "Stateless JWT Auth with HS256"),
            (3, True, "Role-Based Route Guards"),
            # Module 4 lessons (Spring Boot)
            (4, True, "Spring Boot Project Setup & REST Endpoints"),
            (4, True, "Application Properties & Profile Management"),
            # Module 5 lessons
            (5, True, "Spring Data JPA Repositories & Relationships"),
            (5, True, "Stateless Spring Security Filter Chain"),
        ]
        for l in lessons_data:
            db.execute(text("""
                INSERT INTO lessons (module_id, is_published, lesson_title, created_at)
                VALUES (:mid, :pub, :title, NOW())
            """), {"mid": l[0], "pub": l[1], "title": l[2]})

        print("--- Seeding Lesson Contents & Resources ---")
        contents_data = [
            (1, "text", "FastAPI uses Starlette under the hood for asynchronous request handling. Always use `async def` for I/O-bound operations.", 1),
            (1, "code", "from fastapi import FastAPI\napp = FastAPI()\n\n@app.get('/')\nasync def root():\n    return {'status': 'active'}", 2),
            (2, "text", "Pydantic models define schema validation. Use field validators for custom rules such as email and password complexity.", 1),
            (3, "text", "FastAPI dependencies (`Depends`) allow dependency injection for database sessions, auth checks, and caching clients.", 1),
            (4, "text", "Use `create_engine` and `sessionmaker` to manage connection pooling to PostgreSQL.", 1),
            (8, "text", "Spring Boot auto-configures beans based on classpath dependencies. Use `@RestController` and `@RequestMapping` to build REST APIs.", 1),
        ]
        for c in contents_data:
            db.execute(text("""
                INSERT INTO lesson_contents (lesson_id, content_type, content, sequence_number, created_at)
                VALUES (:lid, :ctype, :content, :seq, NOW())
            """), {"lid": c[0], "ctype": c[1], "content": c[2], "seq": c[3]})

        # These are optional examples. Only seed local resources when the
        # referenced file is actually present, so the UI never advertises a
        # download that returns 404.
        resources_data = [
            (1, "FastAPI Complete Architecture Guide", "pdf", "/uploads/resources/fastapi_guide.pdf"),
            (2, "Pydantic v2 Validation Cheatsheet", "pdf", "/uploads/resources/pydantic_cheatsheet.pdf"),
            (4, "SQLAlchemy 2.0 Best Practices", "pdf", "/uploads/resources/sqlalchemy_best_practices.pdf"),
            (8, "Spring Boot 3 Enterprise Guide", "pdf", "/uploads/resources/spring_boot_guide.pdf"),
        ]
        resources_data = [
            r for r in resources_data
            if not r[3].startswith("/uploads/")
            or (BASE_DIR / r[3].lstrip("/")).is_file()
        ]

        for r in resources_data:
            db.execute(text("""
                INSERT INTO resources (lesson_id, resource_name, resource_type, resource_url, created_at)
                VALUES (:lid, :name, :type, :url, NOW())
            """), {"lid": r[0], "name": r[1], "type": r[2], "url": r[3]})

        print("--- Seeding Assignments & Submissions ---")
        now = datetime.datetime.now()
        due1 = now + datetime.timedelta(days=7)
        due2 = now + datetime.timedelta(days=14)
        assignments_data = [
            (1, 1, "Build a CRUD REST API with FastAPI", "Implement a complete RESTful API with validation, CRUD operations, and unit tests.", due1, Decimal("100.00"), Decimal("50.00"), "USR002"),
            (1, 2, "Database Migration & Caching Implementation", "Configure Alembic migrations and implement caching with Valkey.", due2, Decimal("100.00"), Decimal("60.00"), "USR002"),
            (2, 4, "Spring Boot Microservice with JPA", "Build a customer management service with Spring Data JPA and validation.", due1, Decimal("100.00"), Decimal("50.00"), "USR003"),
        ]
        for a in assignments_data:
            db.execute(text("""
                INSERT INTO assignments (course_id, module_id, title, description, due_date, max_marks, passing_marks, created_by, created_at)
                VALUES (:cid, :mid, :title, :desc, :due, :max, :pass, :cb, NOW())
            """), {"cid": a[0], "mid": a[1], "title": a[2], "desc": a[3], "due": a[4], "max": a[5], "pass": a[6], "cb": a[7]})

        submissions_data = [
            (1, 1, now - datetime.timedelta(days=1), "Completed FastAPI CRUD assignment with all tests passing.", "/uploads/assignments/student1_assignment1.pdf", "graded", Decimal("95.00"), 1, "Excellent architecture and test coverage!"),
            (1, 2, now - datetime.timedelta(hours=5), "Submitted my solution with Docker compose and documentation.", "/uploads/assignments/student2_assignment1.pdf", "submitted", None, None, None),
            (3, 3, now - datetime.timedelta(hours=2), "Spring Boot JPA service implemented with custom queries.", None, "submitted", None, None, None),
        ]
        for s in submissions_data:
            db.execute(text("""
                INSERT INTO submissions (assignment_id, student_id, submission_date, submission_text, submission_file, status, marks, graded_by, feedback, created_at)
                VALUES (:aid, :sid, :date, :text, :file, :status, :marks, :gb, :fb, NOW())
            """), {"aid": s[0], "sid": s[1], "date": s[2], "text": s[3], "file": s[4], "status": s[5], "marks": s[6], "gb": s[7], "fb": s[8]})

        print("--- Seeding Quizzes, Questions & Attempts ---")
        quizzes_data = [
            (1, "FastAPI Routing & Dependency Injection Quiz", "Test your knowledge on async endpoints, query parameters, and dependency injection.", Decimal("20.00"), Decimal("10.00"), 15, 2, True),
            (2, "Pydantic Schemas & Validation Quiz", "Test your understanding of Pydantic models, field validation, and serializer methods.", Decimal("15.00"), Decimal("8.00"), 10, 2, True),
            (8, "Spring Boot Core Fundamentals Quiz", "Test your knowledge of Spring IoC container, beans, and annotations.", Decimal("20.00"), Decimal("10.00"), 15, 2, True),
        ]
        for q in quizzes_data:
            db.execute(text("""
                INSERT INTO quizzes (lesson_id, title, description, max_marks, passing_marks, duration_minutes, max_attempts, is_published, created_at)
                VALUES (:lid, :title, :desc, :max, :pass, :dur, :ma, :pub, NOW())
            """), {"lid": q[0], "title": q[1], "desc": q[2], "max": q[3], "pass": q[4], "dur": q[5], "ma": q[6], "pub": q[7]})

        # Questions for Quizzes (quiz_id=1, quiz_id=2, quiz_id=3)
        questions_data = [
            # Quiz 1
            (1, "Which decorator is used to define a GET endpoint in FastAPI?", "multiple_choice", Decimal("5.00")),
            (1, "How do you define a query parameter with a default value in FastAPI?", "multiple_choice", Decimal("5.00")),
            (1, "Which keyword is required when declaring an asynchronous route handler in FastAPI?", "multiple_choice", Decimal("5.00")),
            (1, "What status code is returned by default for successful POST creation?", "multiple_choice", Decimal("5.00")),

            # Quiz 2
            (2, "Which class is the fundamental building block for data validation in Pydantic v2?", "multiple_choice", Decimal("5.00")),
            (2, "Which decorator is used in Pydantic to validate individual fields?", "multiple_choice", Decimal("5.00")),
            (2, "What method exports a Pydantic v2 model to a Python dictionary?", "multiple_choice", Decimal("5.00")),

            # Quiz 3
            (3, "Which annotation marks a class as a Spring Boot REST API controller?", "multiple_choice", Decimal("5.00")),
            (3, "Which annotation is used for automatic dependency injection in Spring?", "multiple_choice", Decimal("5.00")),
            (3, "Which annotation specifies the HTTP POST mapping on a method?", "multiple_choice", Decimal("5.00")),
            (3, "What is the primary interface for CRUD operations in Spring Data JPA?", "multiple_choice", Decimal("5.00")),
        ]
        for q in questions_data:
            db.execute(text("""
                INSERT INTO quiz_questions (quiz_id, question_text, question_type, marks)
                VALUES (:qid, :text, :type, :marks)
            """), {"qid": q[0], "text": q[1], "type": q[2], "marks": q[3]})

        # Options for Questions 1-11
        options_data = [
            # Q1
            (1, "@app.get('/path')", True),
            (1, "@app.route('/path', method='GET')", False),
            (1, "@app.fetch('/path')", False),
            (1, "@app.handle_get('/path')", False),

            # Q2
            (2, "def endpoint(q: str = 'default'):", True),
            (2, "def endpoint(q = Query.default('default')):", False),
            (2, "def endpoint(q: default='default'):", False),
            (2, "def endpoint(query: str == 'default'):", False),

            # Q3
            (3, "async def", True),
            (3, "coroutine def", False),
            (3, "thread def", False),
            (3, "defer def", False),

            # Q4
            (4, "201 Created (or 200 OK)", True),
            (4, "404 Not Found", False),
            (4, "500 Internal Server Error", False),
            (4, "302 Redirect", False),

            # Q5
            (5, "BaseModel", True),
            (5, "DataModel", False),
            (5, "SchemaModel", False),
            (5, "PydanticEntity", False),

            # Q6
            (6, "@field_validator", True),
            (6, "@validator_field", False),
            (6, "@check_field", False),
            (6, "@prop_validator", False),

            # Q7
            (7, "model_dump()", True),
            (7, "to_dict()", False),
            (7, "dict_dump()", False),
            (7, "as_dict()", False),

            # Q8
            (8, "@RestController", True),
            (8, "@ControllerAPI", False),
            (8, "@WebEndpoint", False),
            (8, "@ServiceRest", False),

            # Q9
            (9, "@Autowired", True),
            (9, "@InjectBean", False),
            (9, "@AutoBind", False),
            (9, "@SpringInject", False),

            # Q10
            (10, "@PostMapping", True),
            (10, "@PostRoute", False),
            (10, "@HttpPost", False),
            (10, "@ActionPost", False),

            # Q11
            (11, "JpaRepository", True),
            (11, "CrudBean", False),
            (11, "EntityDao", False),
            (11, "SpringOrmRepository", False),
        ]
        for opt in options_data:
            db.execute(text("""
                INSERT INTO question_options (question_id, option_text, is_correct)
                VALUES (:qid, :text, :cor)
            """), {"qid": opt[0], "text": opt[1], "cor": opt[2]})

        # Quiz attempt for student 1
        db.execute(text("""
            INSERT INTO quiz_attempts (quiz_id, student_id, attempt_number, started_at, submitted_at, marks, status, passed)
            VALUES (1, 1, 1, :start, :sub, 20.00, 'Completed', true)
        """), {"start": now - datetime.timedelta(days=2), "sub": now - datetime.timedelta(days=2, minutes=-12)})

        # Student answers for Attempt 1
        db.execute(text("INSERT INTO student_answers (attempt_id, question_id, selected_option_id, marks_awarded) VALUES (1, 1, 1, 5.00)"))
        db.execute(text("INSERT INTO student_answers (attempt_id, question_id, selected_option_id, marks_awarded) VALUES (1, 2, 5, 5.00)"))
        db.execute(text("INSERT INTO student_answers (attempt_id, question_id, selected_option_id, marks_awarded) VALUES (1, 3, 9, 5.00)"))
        db.execute(text("INSERT INTO student_answers (attempt_id, question_id, selected_option_id, marks_awarded) VALUES (1, 4, 13, 5.00)"))

        print("--- Seeding Class Sessions ---")
        sessions_data = [
            (1, 1, (now + datetime.timedelta(days=2)).date(), datetime.time(10, 0), datetime.time(11, 30), "Live Q&A: FastAPI Async Architecture", "https://meet.google.com/abc-defg-hij"),
            (1, 1, (now + datetime.timedelta(days=5)).date(), datetime.time(14, 0), datetime.time(15, 30), "Deep Dive: Redis Caching and Performance", "https://meet.google.com/xyz-uvwx-rst"),
            (2, 2, (now + datetime.timedelta(days=3)).date(), datetime.time(16, 0), datetime.time(17, 30), "Live Workshop: Spring Security 6 JWT Implementation", "https://teams.microsoft.com/l/meetup-join/12345"),
        ]
        for s in sessions_data:
            db.execute(text("""
                INSERT INTO class_sessions (course_id, teacher_id, session_date, start_time, end_time, topic, meeting_link)
                VALUES (:cid, :tid, :date, :st, :et, :topic, :link)
            """), {"cid": s[0], "tid": s[1], "date": s[2], "st": s[3], "et": s[4], "topic": s[5], "link": s[6]})

        print("--- Seeding Announcements & Discussions ---")
        announcements_data = [
            (1, 1, "USR002", "Welcome to Mastering FastAPI!", "Welcome everyone. Please review Module 1 lessons and set up your Python 3.12+ virtual environment."),
            (1, None, "USR002", "First Live Class Scheduled for Wednesday", "We will hold our first live interactive architecture review this Wednesday at 10:00 AM IST."),
            (2, 3, "USR003", "Welcome to Enterprise Java & Spring Boot 3", "Welcome students. Make sure you have JDK 21 and Docker Desktop installed on your system."),
        ]
        for a in announcements_data:
            db.execute(text("""
                INSERT INTO announcements (course_id, session_id, created_by, title, message, created_at)
                VALUES (:cid, :sid, :cb, :title, :msg, NOW())
            """), {"cid": a[0], "sid": a[1], "cb": a[2], "title": a[3], "msg": a[4]})

        discussions_data = [
            (1, 1, "USR005", None, "How should we handle database connection timeouts in high-concurrency scenarios?", now - datetime.timedelta(days=1)),
            (1, 1, "USR002", 1, "Great question! Configure `pool_size=20, max_overflow=10, pool_recycle=3600` in SQLAlchemy engine.", now - datetime.timedelta(hours=18)),
            (1, 2, "USR006", None, "Is it better to use Pydantic v2 `BaseModel` or dataclasses for request payloads?", now - datetime.timedelta(hours=12)),
            (1, 2, "USR002", 3, "Always use Pydantic BaseModel for API payloads because of automatic validation, serialization, and OpenAPI schema generation.", now - datetime.timedelta(hours=8)),
        ]
        for d in discussions_data:
            db.execute(text("""
                INSERT INTO discussions (course_id, lesson_id, sender_uid, parent_id, message, created_at)
                VALUES (:cid, :lid, :sender, :pid, :msg, :created)
            """), {"cid": d[0], "lid": d[1], "sender": d[2], "pid": d[3], "msg": d[4], "created": d[5]})

        print("--- Seeding Notifications ---")
        notifications_data = [
            ("USR005", 1, None, "session", "Upcoming Live Session", "Live Q&A: FastAPI Async Architecture is scheduled for Wednesday.", "sent", False),
            ("USR005", None, 1, "assignment", "Assignment Due in 7 Days", "Build a CRUD REST API with FastAPI is due on next Tuesday.", "sent", False),
            ("USR005", None, None, "course", "Course Announcement", "Welcome to Mastering FastAPI has been posted by Prof. Riya Sharma.", "sent", True),
            ("USR006", 1, None, "session", "Upcoming Live Session", "Live Q&A: FastAPI Async Architecture is scheduled for Wednesday.", "sent", False),
            ("USR002", None, 1, "submission", "New Assignment Submission", "Student Aarav Jain has submitted assignment 1 for grading.", "sent", False),
            ("USR001", None, None, "system", "System Update", "Database maintenance and Valkey cache flush completed successfully.", "sent", True),
        ]
        for n in notifications_data:
            db.execute(text("""
                INSERT INTO notifications (uid, session_id, assignment_id, notification_type, title, message, status, is_read, created_at)
                VALUES (:uid, :sid, :aid, :ntype, :title, :msg, :status, :read, NOW())
            """), {"uid": n[0], "sid": n[1], "aid": n[2], "ntype": n[3], "title": n[4], "msg": n[5], "status": n[6], "read": n[7]})

        print("--- Seeding Lesson Progress ---")
        progress_data = [
            (1, 1, Decimal("100.00"), True, (now - datetime.timedelta(days=3)).date()),
            (1, 2, Decimal("100.00"), True, (now - datetime.timedelta(days=2)).date()),
            (1, 3, Decimal("60.00"), False, None),
            (2, 1, Decimal("100.00"), True, (now - datetime.timedelta(days=1)).date()),
            (2, 2, Decimal("40.00"), False, None),
            (3, 8, Decimal("100.00"), True, (now - datetime.timedelta(days=1)).date()),
        ]
        for p in progress_data:
            db.execute(text("""
                INSERT INTO lesson_progress (student_id, lesson_id, progress_percentage, completed, completed_date)
                VALUES (:sid, :lid, :pct, :comp, :date)
            """), {"sid": p[0], "lid": p[1], "pct": p[2], "comp": p[3], "date": p[4]})

        print("--- Seeding Audit Logs ---")
        audit_data = [
            ("USR001", "CREATE", "COURSE", "1"),
            ("USR001", "PUBLISH", "COURSE", "1"),
            ("USR002", "CREATE", "ASSIGNMENT", "1"),
            ("USR002", "CREATE", "QUIZ", "1"),
            ("USR005", "SUBMIT", "ASSIGNMENT", "1"),
            ("USR002", "GRADE", "SUBMISSION", "1"),
        ]
        for a in audit_data:
            db.execute(text("""
                INSERT INTO audit_logs (uid, action, entity_type, entity_id, created_at)
                VALUES (:uid, :act, :etype, :eid, NOW())
            """), {"uid": a[0], "act": a[1], "etype": a[2], "eid": a[3]})

        db.commit()
        print("=== Database successfully seeded with rich connected data! ===")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
