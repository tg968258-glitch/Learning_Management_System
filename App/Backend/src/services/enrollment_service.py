from Backend.src.services.filehandler import (
    COURSES_FILE,
    ENROLLMENTS_FILE,
    STUDENTS_FILE,
    load_data,
    save_data,
)
from Backend.src.utils.logger import logger


def get_all_enrollments():

    return load_data(ENROLLMENTS_FILE)


def get_enrollment(enrollment_id):

    enrollments = load_data(ENROLLMENTS_FILE)

    for enrollment in enrollments:

        if enrollment["enrollment_id"] == enrollment_id:
            return enrollment

    return None


def generate_enrollment_id():

    enrollments = load_data(ENROLLMENTS_FILE)

    if not enrollments:
        return 1

    last_id = max(
        enrollment["enrollment_id"]
        for enrollment in enrollments
    )

    return last_id + 1


def create_enrollment(student_id, course_id):

    students = load_data(STUDENTS_FILE)
    courses = load_data(COURSES_FILE)
    enrollments = load_data(ENROLLMENTS_FILE)

    # Check student
    student_exists = any(
        student["student_id"] == student_id
        for student in students
    )

    if not student_exists:

        return {
            "success": False,
            "message": "Student ID does not exist."
        }

    # Check course
    course_exists = any(
        course["course_id"] == course_id
        for course in courses
    )

    if not course_exists:

        return {
            "success": False,
            "message": "Course ID does not exist."
        }

    # Check duplicate enrollment
    for enrollment in enrollments:

        if (
            enrollment["student_id"] == student_id
            and enrollment["course_id"] == course_id
        ):

            return {
                "success": False,
                "message": "Student is already enrolled."
            }

    # Create enrollment
    enrollment = {
        "enrollment_id": generate_enrollment_id(),
        "student_id": student_id,
        "course_id": course_id,
        "status": "pending"
    }

    enrollments.append(enrollment)

    save_data(
        ENROLLMENTS_FILE,
        enrollments
    )

    logger.info(
        f"Student {student_id} enrolled "
        f"in Course {course_id}"
    )

    return {
        "success": True,
        "message": "Enrollment created successfully.",
        "enrollment": enrollment
    }


def update_enrollment(enrollment_id, updated_data):

    enrollments = load_data(ENROLLMENTS_FILE)

    for enrollment in enrollments:

        if enrollment["enrollment_id"] == enrollment_id:

            enrollment.update(updated_data)

            save_data(
                ENROLLMENTS_FILE,
                enrollments
            )

            logger.info(
                f"Enrollment Updated: {enrollment_id}"
            )

            return enrollment

    return None


def delete_enrollment(enrollment_id):

    enrollments = load_data(ENROLLMENTS_FILE)

    for index, enrollment in enumerate(enrollments):

        if enrollment["enrollment_id"] == enrollment_id:

            deleted_enrollment = enrollments.pop(index)

            save_data(
                ENROLLMENTS_FILE,
                enrollments
            )

            logger.info(
                f"Enrollment Deleted: {enrollment_id}"
            )

            return deleted_enrollment

    return None


def approve_enrollment(enrollment_id):

    return update_enrollment(
        enrollment_id,
        {"status": "approved"}
    )


def reject_enrollment(enrollment_id):

    return update_enrollment(
        enrollment_id,
        {"status": "rejected"}
    )


def get_student_enrollments(student_id):

    enrollments = load_data(ENROLLMENTS_FILE)

    return [
        enrollment
        for enrollment in enrollments
        if enrollment["student_id"] == student_id
    ]


def get_course_enrollments(course_id):

    enrollments = load_data(ENROLLMENTS_FILE)

    return [
        enrollment
        for enrollment in enrollments
        if enrollment["course_id"] == course_id
    ]