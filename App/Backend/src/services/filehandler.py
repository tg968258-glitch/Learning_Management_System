import json
import os

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

DATA_DIR = os.path.join(BASE_DIR, "data")


STUDENTS_FILE = os.path.join(DATA_DIR, "students.json")
COURSES_FILE = os.path.join(DATA_DIR, "courses.json")
ENROLLMENTS_FILE = os.path.join(DATA_DIR, "enrollments.json")
TEACHERS_FILE = os.path.join(DATA_DIR, "teachers.json")
ASSIGNMENTS_FILE = os.path.join(DATA_DIR, "assignments.json")
USERS_FILE = os.path.join(DATA_DIR, "users.json")


def load_data(file_path):
    try:
        with open(file_path, "r") as file:
            return json.load(file)

    except FileNotFoundError:
        return []

    except json.JSONDecodeError:
        return []


def save_data(file_path, data):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)