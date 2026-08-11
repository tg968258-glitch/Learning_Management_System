# Learning Management System (LMS) - CLI Application

## Project Overview

The Learning Management System (LMS) is a Command Line Interface (CLI) application developed in Python. It allows users to manage students, courses, and enrollments using JSON files for data storage. The project demonstrates Python programming concepts such as file handling, input validation, exception handling, logging, modular programming, and CRUD operations.

---

## Features

### Student Management
- Add Student
- View Students (Tabular Format)
- Update Student
- Delete Student
- Search Student
- Auto-generated Student ID

### Course Management
- Add Course
- View Courses
- Update Course
- Delete Course
- Search Course
- Auto-generated Course ID

### Enrollment Management
- Enroll Student into Course
- View Enrollments
- Prevent Duplicate Enrollment
- Validate Student and Course IDs

### Validation
- Name Validation
- Email Validation
- Phone Number Validation
- Integer Validation
- Float Validation
- Positive Number Validation
- Percentage Range Validation
- Menu Choice Validation

### Logging
- Logs successful operations
- Logs warnings and errors
- Stores logs in **lms.log**

---

## Technologies Used

- Python 3
- JSON
- Logging Module

---

## Project Structure

```
LMS/
│
├── main.py
├── filehandler.py
├── input_validator.py
├── numeric_validator.py
├── string_sanitizer.py
├── logger.py
│
├── students.json
├── courses.json
├── enrollments.json
│
├── lms.log
└── README.md
```

---

## How to Run

Open Command Prompt or Terminal.

Navigate to the project folder.

```
cd utils
```

Run the application.

```
python main.py
```

---

## Menu

```
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

---

## Data Storage

The application stores data in JSON files.

- students.json
- courses.json
- enrollments.json

No database is required.

---

## Logging

The project creates a log file named:

```
lms.log
```

Example log:

```
2026-08-07 19:10:15 - INFO - Student added successfully.
2026-08-07 19:12:02 - INFO - Course added successfully.
2026-08-07 19:15:50 - INFO - Student enrolled successfully.
2026-08-07 19:18:14 - ERROR - Student ID not found.
```

---

## Python Concepts Used

- Functions
- Modules
- JSON File Handling
- CRUD Operations
- Exception Handling
- Logging
- Input Validation
- While Loops
- Conditional Statements
- Dictionaries
- Lists

---

## Future Enhancements

- Login Authentication
- Faculty Module
- Marks Management
- Attendance Management
- Course Completion Status
- CSV Export
- SQLite Database Integration
- Colorful CLI Interface

---

## Author

Developed by Tanvi Gupta
