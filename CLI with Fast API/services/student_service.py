from filehandler import (
    load_students,
    search_student,
    add_student,
    update_student,
    delete_student
)


def get_all_students():
    return load_students()


def get_student(student_id):
    student = search_student(student_id)

    if not student:
        return None

    return student


def create_student(student):
    add_student(student)
    return student


def update_student_data(student_id, updated_data):
    student = search_student(student_id)

    if not student:
        return None

    update_student(student_id, updated_data)

    return search_student(student_id)


def remove_student(student_id):
    student = search_student(student_id)

    if not student:
        return False

    delete_student(student_id)
    return True