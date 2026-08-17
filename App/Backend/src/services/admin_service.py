from Backend.src.services.filehandler import (
    ASSIGNMENTS_FILE,
    COURSES_FILE,
    ENROLLMENTS_FILE,
    STUDENTS_FILE,
    TEACHERS_FILE,
    load_data,
)


def get_dashboard_data():

    students = load_data(STUDENTS_FILE)
    courses = load_data(COURSES_FILE)
    enrollments = load_data(ENROLLMENTS_FILE)
    teachers = load_data(TEACHERS_FILE)
    assignments = load_data(ASSIGNMENTS_FILE)

    return {
        "total_students": len(students),
        "total_teachers": len(teachers),
        "total_courses": len(courses),
        "total_enrollments": len(enrollments),
        "total_assignments": len(assignments)
    }