from Backend.src.services.filehandler import (
    STUDENTS_FILE,
    load_data,
    save_data
)

from Backend.src.utils.logger import logger


def get_all_students():
    return load_data(STUDENTS_FILE)


def get_student(student_id):
    students = load_data(STUDENTS_FILE)

    for student in students:
        if student["student_id"] == student_id:
            return student

    return None


def generate_student_id():
    students = load_data(STUDENTS_FILE)

    if not students:
        return 101

    last_id = max(
        student["student_id"]
        for student in students
    )

    return last_id + 1


def create_student(student_data):

    students = load_data(STUDENTS_FILE)

    # Generate ID
    student_id = generate_student_id()

    student_data["student_id"] = student_id

    students.append(student_data)

    save_data(STUDENTS_FILE, students)

    logger.info(
        f"Student Added: {student_id}"
    )

    return student_data


def update_student(student_id, updated_data):

    students = load_data(STUDENTS_FILE)

    for student in students:

        if student["student_id"] == student_id:

            student.update(updated_data)

            save_data(STUDENTS_FILE, students)

            logger.info(
                f"Student Updated: {student_id}"
            )

            return student

    return None


def delete_student(student_id):

    students = load_data(STUDENTS_FILE)

    for index, student in enumerate(students):

        if student["student_id"] == student_id:

            deleted_student = students.pop(index)

            save_data(STUDENTS_FILE, students)

            logger.info(
                f"Student Deleted: {student_id}"
            )

            return deleted_student

    return None