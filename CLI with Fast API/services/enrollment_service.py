from filehandler import (
    load_enrollments,
    enroll_student,
    search_student,
    search_course
)


def get_all_enrollments():
    return load_enrollments()


def create_enrollment(student_id, course_id):

    student = search_student(student_id)

    if not student:
        return {
            "success": False,
            "message": "Student ID does not exist."
        }

    course = search_course(course_id)

    if not course:
        return {
            "success": False,
            "message": "Course ID does not exist."
        }

    message = enroll_student(student_id, course_id)

    return {
        "success": True,
        "message": message
    }