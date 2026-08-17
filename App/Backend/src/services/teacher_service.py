from Backend.src.services.filehandler import TEACHERS_FILE, load_data, save_data
from Backend.src.utils.logger import logger


def get_all_teachers():

    return load_data(TEACHERS_FILE)


def get_teacher(teacher_id):

    teachers = load_data(TEACHERS_FILE)

    for teacher in teachers:

        if teacher["teacher_id"] == teacher_id:
            return teacher

    return None


def generate_teacher_id():

    teachers = load_data(TEACHERS_FILE)

    if not teachers:
        return 301

    last_id = max(
        teacher["teacher_id"]
        for teacher in teachers
    )

    return last_id + 1


def create_teacher(teacher_data):

    teachers = load_data(TEACHERS_FILE)

    # Generate teacher ID
    teacher_id = generate_teacher_id()

    teacher_data["teacher_id"] = teacher_id

    teachers.append(teacher_data)

    save_data(
        TEACHERS_FILE,
        teachers
    )

    logger.info(
        f"Teacher Added: {teacher_id}"
    )

    return teacher_data


def update_teacher(teacher_id, updated_data):

    teachers = load_data(TEACHERS_FILE)

    for teacher in teachers:

        if teacher["teacher_id"] == teacher_id:

            # Do not allow teacher ID to be changed
            updated_data.pop("teacher_id", None)

            teacher.update(updated_data)

            save_data(
                TEACHERS_FILE,
                teachers
            )

            logger.info(
                f"Teacher Updated: {teacher_id}"
            )

            return teacher

    return None


def delete_teacher(teacher_id):

    teachers = load_data(TEACHERS_FILE)

    for index, teacher in enumerate(teachers):

        if teacher["teacher_id"] == teacher_id:

            deleted_teacher = teachers.pop(index)

            save_data(
                TEACHERS_FILE,
                teachers
            )

            logger.info(
                f"Teacher Deleted: {teacher_id}"
            )

            return deleted_teacher

    return None