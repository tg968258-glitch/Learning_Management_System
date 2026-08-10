# Learning Management System (LMS)

A Python-based **Learning Management System (LMS)** that provides both a **Command Line Interface (CLI)** and a **FastAPI REST API** for managing students, courses, and enrollments.

---

## Project Overview

The LMS allows users to manage:

* Students
* Courses
* Enrollments

The application can be used in two ways:

1. **CLI Application** – Manage LMS data directly from the terminal.
2. **FastAPI REST API** – Access LMS functionality through HTTP endpoints and API clients such as Swagger UI, Postman, or `curl`.

The application currently uses **JSON files for data persistence**, so no database is required.

---

# Features

## Student Management

* Add Student
* View Students
* Update Student
* Delete Student
* Search Student
* Auto-generated Student ID
* Input validation

## Course Management

* Add Course
* View Courses
* Update Course
* Delete Course
* Search Course
* Auto-generated Course ID
* Input validation

## Enrollment Management

* Enroll Student into Course
* View Enrollments
* Prevent Duplicate Enrollment
* Validate Student ID
* Validate Course ID

---

# CLI Application

The CLI provides an interactive menu for managing LMS data directly from the terminal.

### CLI Menu

```text
1. Add Student
2. View Students
3. Update Student
4. Delete Student
5. Search Student

6. Add Course
7. View Courses
8. Update Course
9. Delete Course
10. Search Course

11. Enroll Student
12. View Enrollments

13. Exit
```

### CLI Features

* Interactive terminal menu
* CRUD operations
* Tabular data display
* Input validation
* Exception handling
* Logging
* JSON file storage
* Auto-generated IDs

---

# FastAPI REST API

The LMS also provides a RESTful API built using **FastAPI**.

The API exposes endpoints for managing students, courses, and enrollments.

### API Modules

```text
Student API
├── Create Student
├── Get Students
├── Get Student by ID
├── Update Student
└── Delete Student

Course API
├── Create Course
├── Get Courses
├── Get Course by ID
├── Update Course
└── Delete Course

Enrollment API
├── Create Enrollment
├── Get Enrollments
└── Validate Student and Course
```

---

## API Documentation

FastAPI automatically provides interactive API documentation.

### Swagger UI

When the FastAPI server is running, open:

```text
http://127.0.0.1:8000/docs
```


---

# Technologies Used

### Backend

* Python 3
* FastAPI
* Uvicorn

### Data Storage

* JSON
* Python File Handling

### Development Concepts

* REST API
* CRUD Operations
* Modular Programming
* Input Validation
* Exception Handling
* Logging
* HTTP Methods
* JSON Request/Response Handling

---

# Data Storage

The application currently uses JSON files instead of a database.

```text
students.json
courses.json
enrollments.json
```



# Author

**Tanvi Gupta**

