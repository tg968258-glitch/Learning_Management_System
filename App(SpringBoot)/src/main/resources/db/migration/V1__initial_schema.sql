-- ============================================================
-- V1__initial_schema.sql
-- LMS Database Schema (mirrored from FastAPI SQLAlchemy models)
-- ============================================================

-- ─── USERS ───────────────────────────────────────────────────
CREATE TABLE users (
    uid             VARCHAR(10)  PRIMARY KEY,
    username        VARCHAR(50)  NOT NULL UNIQUE,
    email           VARCHAR(255) NOT NULL UNIQUE,
    recovery_email  VARCHAR(255),
    password_hash   VARCHAR(255) NOT NULL,
    role            VARCHAR(20)  NOT NULL,
    email_verified            BOOLEAN NOT NULL DEFAULT FALSE,
    recovery_email_verified   BOOLEAN NOT NULL DEFAULT FALSE,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    deactivated_at  TIMESTAMP
);

-- ─── OTP VERIFICATIONS ───────────────────────────────────────
CREATE TABLE otp_verifications (
    otp_id      SERIAL      PRIMARY KEY,
    uid         VARCHAR(10) NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    otp_hash    VARCHAR(255) NOT NULL,
    purpose     VARCHAR(30)  NOT NULL,
    expires_at  TIMESTAMP    NOT NULL,
    attempts    INTEGER      NOT NULL DEFAULT 0,
    is_used     BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- ─── USER SESSIONS ───────────────────────────────────────────
CREATE TABLE user_sessions (
    session_id          VARCHAR(100) PRIMARY KEY,
    uid                 VARCHAR(10)  NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    refresh_token_hash  VARCHAR(255) NOT NULL,
    created_at          TIMESTAMP    NOT NULL DEFAULT NOW(),
    expires_at          TIMESTAMP    NOT NULL,
    last_used_at        TIMESTAMP,
    revoked             BOOLEAN      NOT NULL DEFAULT FALSE
);

-- ─── STUDENTS ────────────────────────────────────────────────
CREATE TABLE students (
    student_id    SERIAL      PRIMARY KEY,
    uid           VARCHAR(10) NOT NULL UNIQUE REFERENCES users(uid) ON DELETE CASCADE,
    name          VARCHAR(100) NOT NULL,
    date_of_birth DATE,
    gender        VARCHAR(20),
    phone_number  VARCHAR(15)
);

-- ─── TEACHERS ────────────────────────────────────────────────
CREATE TABLE teachers (
    teacher_id     SERIAL      PRIMARY KEY,
    uid            VARCHAR(10) NOT NULL UNIQUE REFERENCES users(uid) ON DELETE CASCADE,
    name           VARCHAR(100) NOT NULL,
    phone_number   VARCHAR(15),
    specialization VARCHAR(100),
    qualification  VARCHAR(150),
    experience     INTEGER
);

-- ─── TEACHER INVITATIONS ─────────────────────────────────────
CREATE TABLE teacher_invitations (
    invitation_id SERIAL      PRIMARY KEY,
    email         VARCHAR(255) NOT NULL,
    token_hash    VARCHAR(255) NOT NULL UNIQUE,
    invited_by    VARCHAR(10)  NOT NULL REFERENCES users(uid),
    expires_at    TIMESTAMP    NOT NULL,
    is_used       BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at    TIMESTAMP    NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_teacher_invitations_email ON teacher_invitations(email);

-- ─── COURSES ─────────────────────────────────────────────────
CREATE TABLE courses (
    course_id    SERIAL       PRIMARY KEY,
    course_name  VARCHAR(100) NOT NULL,
    description  TEXT,
    duration     VARCHAR(50),
    status       VARCHAR(20)  NOT NULL DEFAULT 'draft',
    category     VARCHAR(100),
    created_by   VARCHAR(10)  REFERENCES users(uid),
    published_by VARCHAR(10)  REFERENCES users(uid),
    created_at   TIMESTAMP    DEFAULT NOW(),
    updated_at   TIMESTAMP
);

-- ─── COURSE TEACHERS (composite PK join table) ───────────────
CREATE TABLE course_teachers (
    course_id       INTEGER NOT NULL REFERENCES courses(course_id) ON DELETE CASCADE,
    teacher_id      INTEGER NOT NULL REFERENCES teachers(teacher_id) ON DELETE CASCADE,
    is_course_admin BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (course_id, teacher_id)
);

-- ─── ENROLLMENTS ─────────────────────────────────────────────
CREATE TABLE enrollments (
    enrollment_id   SERIAL  PRIMARY KEY,
    student_id      INTEGER NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    course_id       INTEGER NOT NULL REFERENCES courses(course_id) ON DELETE CASCADE,
    enrollment_date DATE,
    status          VARCHAR(20) NOT NULL DEFAULT 'active',
    CONSTRAINT uq_student_course UNIQUE (student_id, course_id)
);

-- ─── MODULES ─────────────────────────────────────────────────
CREATE TABLE modules (
    module_id    SERIAL       PRIMARY KEY,
    course_id    INTEGER      NOT NULL REFERENCES courses(course_id) ON DELETE CASCADE,
    is_published BOOLEAN      NOT NULL DEFAULT FALSE,
    published_by VARCHAR(10)  REFERENCES users(uid),
    module_name  VARCHAR(150) NOT NULL,
    description  TEXT
);

-- ─── LESSONS ─────────────────────────────────────────────────
CREATE TABLE lessons (
    lesson_id     SERIAL       PRIMARY KEY,
    module_id     INTEGER      NOT NULL REFERENCES modules(module_id) ON DELETE CASCADE,
    is_published  BOOLEAN      NOT NULL DEFAULT FALSE,
    lesson_title  VARCHAR(150) NOT NULL,
    created_at    TIMESTAMP    DEFAULT NOW(),
    updated_at    TIMESTAMP
);

-- ─── LESSON CONTENTS ─────────────────────────────────────────
CREATE TABLE lesson_contents (
    content_id      SERIAL  PRIMARY KEY,
    lesson_id       INTEGER NOT NULL REFERENCES lessons(lesson_id) ON DELETE CASCADE,
    content_type    VARCHAR(30) NOT NULL,
    content         TEXT        NOT NULL,
    sequence_number INTEGER     NOT NULL,
    created_at      TIMESTAMP   DEFAULT NOW(),
    updated_at      TIMESTAMP
);

-- ─── RESOURCES ───────────────────────────────────────────────
CREATE TABLE resources (
    resource_id   SERIAL       PRIMARY KEY,
    lesson_id     INTEGER      NOT NULL REFERENCES lessons(lesson_id) ON DELETE CASCADE,
    resource_name VARCHAR(150) NOT NULL,
    resource_type VARCHAR(50),
    resource_url  VARCHAR(500) NOT NULL,
    created_at    TIMESTAMP    NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMP
);

-- ─── ASSIGNMENTS ─────────────────────────────────────────────
CREATE TABLE assignments (
    assignment_id SERIAL       PRIMARY KEY,
    course_id     INTEGER      NOT NULL REFERENCES courses(course_id) ON DELETE CASCADE,
    module_id     INTEGER      NOT NULL REFERENCES modules(module_id) ON DELETE CASCADE,
    title         VARCHAR(150) NOT NULL,
    description   TEXT,
    due_date      TIMESTAMP    NOT NULL,
    max_marks     NUMERIC(6,2) NOT NULL,
    passing_marks NUMERIC(6,2) NOT NULL,
    created_by    VARCHAR(10)  NOT NULL REFERENCES users(uid),
    created_at    TIMESTAMP    NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMP
);

-- ─── SUBMISSIONS ─────────────────────────────────────────────
CREATE TABLE submissions (
    submission_id   SERIAL       PRIMARY KEY,
    assignment_id   INTEGER      NOT NULL REFERENCES assignments(assignment_id) ON DELETE CASCADE,
    student_id      INTEGER      NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    submission_date TIMESTAMP,
    submission_text TEXT,
    submission_file VARCHAR(500),
    status          VARCHAR(30)  NOT NULL DEFAULT 'submitted',
    marks           NUMERIC(6,2),
    graded_by       INTEGER      REFERENCES teachers(teacher_id),
    feedback        TEXT,
    created_at      TIMESTAMP    NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP,
    CONSTRAINT uq_assignment_student UNIQUE (assignment_id, student_id)
);

-- ─── QUIZZES ─────────────────────────────────────────────────
CREATE TABLE quizzes (
    quiz_id          SERIAL       PRIMARY KEY,
    lesson_id        INTEGER      NOT NULL REFERENCES lessons(lesson_id) ON DELETE CASCADE,
    title            VARCHAR(150) NOT NULL,
    description      TEXT,
    max_marks        NUMERIC(6,2) NOT NULL,
    passing_marks    NUMERIC(6,2) NOT NULL,
    duration_minutes INTEGER,
    max_attempts     INTEGER      NOT NULL DEFAULT 1,
    is_published     BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at       TIMESTAMP    NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMP
);

-- ─── QUIZ QUESTIONS ──────────────────────────────────────────
CREATE TABLE quiz_questions (
    question_id   SERIAL       PRIMARY KEY,
    quiz_id       INTEGER      NOT NULL REFERENCES quizzes(quiz_id) ON DELETE CASCADE,
    question_text TEXT         NOT NULL,
    question_type VARCHAR(30)  NOT NULL,
    marks         NUMERIC(6,2) NOT NULL
);

-- ─── QUESTION OPTIONS ────────────────────────────────────────
CREATE TABLE question_options (
    option_id   SERIAL  PRIMARY KEY,
    question_id INTEGER NOT NULL REFERENCES quiz_questions(question_id) ON DELETE CASCADE,
    option_text TEXT    NOT NULL,
    is_correct  BOOLEAN NOT NULL DEFAULT FALSE
);

-- ─── QUIZ ATTEMPTS ───────────────────────────────────────────
CREATE TABLE quiz_attempts (
    attempt_id     SERIAL       PRIMARY KEY,
    quiz_id        INTEGER      NOT NULL REFERENCES quizzes(quiz_id) ON DELETE CASCADE,
    student_id     INTEGER      NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    attempt_number INTEGER      NOT NULL,
    started_at     TIMESTAMP,
    submitted_at   TIMESTAMP,
    marks          NUMERIC(6,2),
    status         VARCHAR(20)  NOT NULL DEFAULT 'Not Attempted',
    passed         BOOLEAN,
    CONSTRAINT uq_quiz_student_attempt UNIQUE (quiz_id, student_id, attempt_number)
);

-- ─── STUDENT ANSWERS ─────────────────────────────────────────
CREATE TABLE student_answers (
    answer_id          SERIAL       PRIMARY KEY,
    attempt_id         INTEGER      NOT NULL REFERENCES quiz_attempts(attempt_id) ON DELETE CASCADE,
    question_id        INTEGER      NOT NULL REFERENCES quiz_questions(question_id) ON DELETE CASCADE,
    selected_option_id INTEGER      REFERENCES question_options(option_id),
    marks_awarded      NUMERIC(6,2),
    CONSTRAINT uq_attempt_question UNIQUE (attempt_id, question_id)
);

-- ─── CLASS SESSIONS ──────────────────────────────────────────
CREATE TABLE class_sessions (
    session_id   SERIAL  PRIMARY KEY,
    course_id    INTEGER NOT NULL REFERENCES courses(course_id) ON DELETE CASCADE,
    teacher_id   INTEGER REFERENCES teachers(teacher_id),
    session_date DATE    NOT NULL,
    start_time   TIME,
    end_time     TIME,
    topic        VARCHAR(200)
);

-- ─── DISCUSSIONS ─────────────────────────────────────────────
CREATE TABLE discussions (
    discussion_id SERIAL      PRIMARY KEY,
    course_id     INTEGER     NOT NULL REFERENCES courses(course_id) ON DELETE CASCADE,
    lesson_id     INTEGER     REFERENCES lessons(lesson_id) ON DELETE SET NULL,
    sender_uid    VARCHAR(10) NOT NULL REFERENCES users(uid),
    parent_id     INTEGER     REFERENCES discussions(discussion_id) ON DELETE SET NULL,
    message       TEXT        NOT NULL,
    created_at    TIMESTAMP   NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMP
);

-- ─── ANNOUNCEMENTS ───────────────────────────────────────────
CREATE TABLE announcements (
    announcement_id SERIAL      PRIMARY KEY,
    course_id       INTEGER     NOT NULL REFERENCES courses(course_id) ON DELETE CASCADE,
    session_id      INTEGER     REFERENCES class_sessions(session_id) ON DELETE SET NULL,
    created_by      VARCHAR(10) NOT NULL REFERENCES users(uid),
    title           VARCHAR(150) NOT NULL,
    message         TEXT         NOT NULL,
    created_at      TIMESTAMP    NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP
);

-- ─── NOTIFICATIONS ───────────────────────────────────────────
CREATE TABLE notifications (
    notification_id   SERIAL       PRIMARY KEY,
    uid               VARCHAR(10)  NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    session_id        INTEGER      REFERENCES class_sessions(session_id) ON DELETE SET NULL,
    assignment_id     INTEGER      REFERENCES assignments(assignment_id) ON DELETE SET NULL,
    notification_type VARCHAR(50)  NOT NULL,
    title             VARCHAR(150),
    message           TEXT         NOT NULL,
    status            VARCHAR(20)  NOT NULL DEFAULT 'pending',
    is_read           BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at        TIMESTAMP    DEFAULT NOW(),
    sent_at           TIMESTAMP
);

-- ─── LESSON PROGRESS ─────────────────────────────────────────
CREATE TABLE lesson_progress (
    student_id           INTEGER      NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    lesson_id            INTEGER      NOT NULL REFERENCES lessons(lesson_id) ON DELETE CASCADE,
    progress_percentage  NUMERIC(5,2) NOT NULL DEFAULT 0,
    completed            BOOLEAN      NOT NULL DEFAULT FALSE,
    completed_date       DATE,
    PRIMARY KEY (student_id, lesson_id)
);

-- ─── AUDIT LOGS ──────────────────────────────────────────────
CREATE TABLE audit_logs (
    audit_id    SERIAL      PRIMARY KEY,
    uid         VARCHAR(10) NOT NULL REFERENCES users(uid),
    action      VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id   VARCHAR(50),
    created_at  TIMESTAMP   NOT NULL DEFAULT NOW()
);
