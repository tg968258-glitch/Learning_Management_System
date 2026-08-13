from Backend.src.services.filehandler import (
    COURSES_FILE,
    load_data,
    save_data
)

from Backend.src.utils.logger import logger


def get_all_courses():
    return load_data(COURSES_FILE)


def get_course(course_id):

    courses = load_data(COURSES_FILE)

    for course in courses:

        if course["course_id"] == course_id:
            return course

    return None


def generate_course_id():

    courses = load_data(COURSES_FILE)

    if not courses:
        return 201

    last_id = max(
        course["course_id"]
        for course in courses
    )

    return last_id + 1


def create_course(course_data):

    courses = load_data(COURSES_FILE)

    course_id = generate_course_id()

    course_data["course_id"] = course_id

    # Default syllabus
    if "syllabus" not in course_data:
        course_data["syllabus"] = []

    courses.append(course_data)

    save_data(COURSES_FILE, courses)

    logger.info(
        f"Course Added: {course_id}"
    )

    return course_data


def update_course(course_id, updated_data):

    courses = load_data(COURSES_FILE)

    for course in courses:

        if course["course_id"] == course_id:

            course.update(updated_data)

            save_data(COURSES_FILE, courses)

            logger.info(
                f"Course Updated: {course_id}"
            )

            return course

    return None


def delete_course(course_id):

    courses = load_data(COURSES_FILE)

    for index, course in enumerate(courses):

        if course["course_id"] == course_id:

            deleted_course = courses.pop(index)

            save_data(COURSES_FILE, courses)

            logger.info(
                f"Course Deleted: {course_id}"
            )

            return deleted_course

    return None


# =========================
# SYLLABUS
# =========================

def get_course_syllabus(course_id):

    course = get_course(course_id)

    if not course:
        return None

    return course.get("syllabus", [])


def update_course_syllabus(course_id, syllabus):

    courses = load_data(COURSES_FILE)

    for course in courses:

        if course["course_id"] == course_id:

            course["syllabus"] = syllabus

            save_data(COURSES_FILE, courses)

            logger.info(
                f"Syllabus Updated: Course {course_id}"
            )

            return course

    return None