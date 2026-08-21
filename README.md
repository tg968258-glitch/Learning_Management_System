# LMS-Documentation
# Learning Management System (LMS)

A backend-based **Learning Management System (LMS)** built using **FastAPI, SQLAlchemy, and PostgreSQL**.

The system provides APIs for managing students, teachers, courses, enrollments, assignments, quizzes, learning content, progress, authentication, and communication.

---

## Tech Stack

- **Backend:** Python, FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Validation:** Pydantic
- **Authentication:** JWT, Password Hashing, OTP Verification
- **Testing:** Pytest
- **Linting:** Ruff
- **Version Control:** Git & GitHub

---

## Features

### Authentication
- User registration and login
- Separate admin login
- JWT authentication
- Role-based access control
- Remember Me and user sessions
- Email and OTP verification
- Forgot and reset password
- Account activation/deactivation

### User Management
- Student profile management
- Teacher profile management
- Admin dashboard
- Role-based permissions

### Course & Learning Management
- Course management
- Student enrollment
- Modules and lessons
- Assignments and submissions
- Assignment grading and feedback
- Quiz management
- Student progress tracking
- Class sessions

### Communication
- Announcements
- Discussions
- Notifications
- Audit logging

---

## Architecture

The backend follows a layered architecture:

```text
Routes
   ↓
Services
   ↓
SQLAlchemy Models
   ↓
PostgreSQL
```

- **Routes** – Handle API requests and responses
- **Schemas** – Validate request data using Pydantic
- **Services** – Contain business logic
- **Models** – Represent PostgreSQL database tables
- **Core** – Authentication, authorization, security, and OTP utilities

---

## Database

The LMS uses **PostgreSQL** with **SQLAlchemy ORM**.

Major entities include:

- Users
- Students
- Teachers
- Courses
- Enrollments
- Modules
- Lessons
- Assignments
- Quizzes
- Progress
- Class Sessions
- Announcements
- Discussions
- Notifications
- Audit Logs
- OTP Verifications
- User Sessions

---

## API Groups

```text
/auth
/admin
/students
/teachers
/courses
/enrollments
/modules
/lessons
/assignments
/quizzes
/progress
/sessions
/announcements
/discussions
/notifications
/audit
```

FastAPI provides interactive API documentation at:

```text
http://127.0.0.1:8000/docs
```

---

## Installation

Clone the repository and move to the application directory:

```bash
git clone <repository-url>
cd Learning_Management_System/App
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file using `.env.example` and configure the required environment variables.

---

## Run the Application

```bash
python -m uvicorn Backend.src.api_main:app --reload
```

Open Swagger UI:

```text
http://127.0.0.1:8000/docs
```

---

## REST API Endpoints

### 1. Get All Courses
```
GET https://lms.com/api/v1/courses
```

### 2. Get Student by ID
```
GET https://lms.com/api/v1/students/{id}
```

### 3. Enroll Student in Course
```
POST https://lms.com/api/v1/enrollments
```

### 4. Get Assignment History
```
GET https://lms.com/api/v1/assignments/history
```

### 5. AI Learning Recommendations
```
POST https://lms.com/api/v1/ai/recommendations
```

---



---

## Features

- User Authentication
- Course Management
- Student Enrollment
- Assignment Management
- Progress Tracking
- AI-Based Learning Recommendations
- Admin Dashboard
- Secure REST APIs

---




## Development Status

The LMS backend is currently being developed and tested module by module.

---

## Author

Developed as a backend Learning Management System project using **Python, FastAPI, SQLAlchemy, and PostgreSQL**.




