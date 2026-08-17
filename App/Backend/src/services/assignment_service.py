from Backend.src.services.filehandler import ASSIGNMENTS_FILE, load_data, save_data
from Backend.src.utils.logger import logger


def get_all_assignments():
    return load_data(ASSIGNMENTS_FILE)


def get_assignment_by_id(assignment_id):
    assignments = load_data(ASSIGNMENTS_FILE)

    for assignment in assignments:
        if assignment["assignment_id"] == assignment_id:
            return assignment

    return None


def get_assignments_by_course(course_id):
    assignments = load_data(ASSIGNMENTS_FILE)

    return [
        assignment
        for assignment in assignments
        if assignment["course_id"] == course_id
    ]


def create_assignment(assignment):
    assignments = load_data(ASSIGNMENTS_FILE)

    if get_assignment_by_id(assignment["assignment_id"]):
        raise ValueError("Assignment ID already exists")

    assignments.append(assignment)

    save_data(ASSIGNMENTS_FILE, assignments)

    logger.info(
        f"Assignment created: {assignment['assignment_id']}"
    )

    return assignment


def update_assignment(assignment_id, updated_assignment):
    assignments = load_data(ASSIGNMENTS_FILE)

    for index, assignment in enumerate(assignments):
        if assignment["assignment_id"] == assignment_id:

            updated_assignment["assignment_id"] = assignment_id

            assignments[index] = updated_assignment

            save_data(ASSIGNMENTS_FILE, assignments)

            logger.info(
                f"Assignment updated: {assignment_id}"
            )

            return updated_assignment

    return None


def delete_assignment(assignment_id):
    assignments = load_data(ASSIGNMENTS_FILE)

    for assignment in assignments:
        if assignment["assignment_id"] == assignment_id:

            assignments.remove(assignment)

            save_data(ASSIGNMENTS_FILE, assignments)

            logger.info(
                f"Assignment deleted: {assignment_id}"
            )

            return True

    return False

def submit_assignment(assignment_id, submission):
    assignments = load_data(ASSIGNMENTS_FILE)

    for assignment in assignments:
        if assignment["assignment_id"] == assignment_id:

            # Prevent duplicate submission by same student
            for existing_submission in assignment.get("submissions", []):
                if existing_submission["student_id"] == submission["student_id"]:
                    raise ValueError(
                        "Student has already submitted this assignment"
                    )

            assignment.setdefault("submissions", [])
            assignment["submissions"].append(submission)

            save_data(ASSIGNMENTS_FILE, assignments)

            logger.info(
                f"Student {submission['student_id']} submitted "
                f"assignment {assignment_id}"
            )

            return submission

    return None


def get_assignment_submissions(assignment_id):
    assignments = load_data(ASSIGNMENTS_FILE)

    for assignment in assignments:
        if assignment["assignment_id"] == assignment_id:
            return assignment.get("submissions", [])

    return None


def update_submission(assignment_id, student_id, updated_submission):
    assignments = load_data(ASSIGNMENTS_FILE)

    for assignment in assignments:
        if assignment["assignment_id"] == assignment_id:

            for index, submission in enumerate(
                assignment.get("submissions", [])
            ):

                if submission["student_id"] == student_id:

                    assignment["submissions"][index] = updated_submission

                    save_data(ASSIGNMENTS_FILE, assignments)

                    logger.info(
                        f"Submission updated for student {student_id} "
                        f"on assignment {assignment_id}"
                    )

                    return updated_submission

    return None