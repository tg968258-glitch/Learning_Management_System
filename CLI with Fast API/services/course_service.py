from filehandler import (
    load_courses,
    search_course,
    add_course,
    update_course,
    delete_course
)


def get_all_courses():
    return load_courses()


def get_course(course_id):
    course = search_course(course_id)

    if not course:
        return None

    return course


def create_course(course):
    add_course(course)
    return course


def update_course_data(course_id, updated_data):
    course = search_course(course_id)

    if not course:
        return None

    update_course(course_id, updated_data)

    return search_course(course_id)


def remove_course(course_id):
    course = search_course(course_id)

    if not course:
        return False

    delete_course(course_id)
    return True