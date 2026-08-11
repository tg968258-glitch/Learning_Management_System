import json
import os
from utils.logger import logger
from tabulate import tabulate
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

file_name = os.path.join(BASE_DIR, "students.json")
courses_file = os.path.join(BASE_DIR, "courses.json")
enrollment_file = os.path.join(BASE_DIR, "enrollments.json")


def load_students():
    try:
        with open(file_name, "r") as file:
            students = json.load(file)

        
        return students

    except FileNotFoundError:
        print("File not found")
        return []

    except json.JSONDecodeError:
        print("Invalid JSON")
        return []


def save_students(students):
   
    try:
        with open(file_name, "w") as file:
            json.dump(students, file, indent=4)

    except Exception as e:
        print(f"Error saving students: {e}")


def add_student(new_student):
    
    students = load_students()

    students.append(new_student)

    save_students(students)
    logger.info(f"Student Added: {new_student['student_id']}")


def view_students():

    students = load_students()

    if not students:
        print("No students found.")
        return

    table = []

    for student in students:
        table.append({
            "Student ID": student["student_id"],
            "Name": student["name"],
            "Age": student["age"],
            "Gender": student["gender"],
            "Email": student["email"],
            "Phone": student["phone_number"],
            "Percentage": student["percentage"]
        })

    print(tabulate(table, headers="keys", tablefmt="grid"))
       


def update_student(student_id, updated_data):
    
    students = load_students()

    for student in students:
        if student["student_id"] == student_id:
            student.update(updated_data)
            save_students(students)
            logger.info(f"Student Updated: {student_id}")
            return True
            
    logger.warning(f"Student Not Found: {student_id}")
    return False
 

def delete_student(student_id):
   
    students = load_students()

    for student in students:
        if student["student_id"] == student_id:
            students.remove(student)
            save_students(students)
            logger.info(f"Student Deleted: {student_id}")
            return True
        logger.warning(f"Student Not Found: {student_id}")
    return False


def search_student(student_id):
    
    students = load_students()

    for student in students:
        if student["student_id"] == student_id:
            return student

    return None

def generate_student_id():
   
    students = load_students()

    if not students:
        return 101

    last_id = max(student["student_id"] for student in students)
    return last_id + 1

def load_courses():
    try:
        with open(courses_file, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def generate_course_id():
    courses = load_courses()

    if not courses:
        return 201

    last_id = max(course["course_id"] for course in courses)
    return last_id + 1

def save_courses(courses):
    with open(courses_file, "w") as file:
        json.dump(courses, file, indent=4)

def add_course(new_course):
    courses = load_courses()
    courses.append(new_course)
    save_courses(courses)
    logger.info(f"Course Added: {new_course['course_id']}")

def view_courses():

    courses = load_courses()

    if not courses:
        print("No courses found.")
        return

    table = []

    for course in courses:
        table.append({
            "Course ID": course["course_id"],
            "Course Name": course["course_name"],
            "Trainer": course["trainer"],
            "Duration": course["duration"]
        })

    print(tabulate(table, headers="keys", tablefmt="grid"))


def search_course(course_id):
    courses = load_courses()

    for course in courses:
        if course["course_id"] == course_id:
          
            return course

    return None

def update_course(course_id, updated_data):
    courses = load_courses()

    for course in courses:
        if course["course_id"] == course_id:
            course.update(updated_data)
            save_courses(courses)
            logger.info(f"Course Updated: {course_id}")
            return True

    return False

def delete_course(course_id):
    courses = load_courses()

    for course in courses:
        if course["course_id"] == course_id:
            courses.remove(course)
            save_courses(courses)
            logger.info(f"Course Deleted: {course_id}")
            return True

    return False

def load_enrollments():
    try:
        with open(enrollment_file, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_enrollments(enrollments):
    with open(enrollment_file, "w") as file:
        json.dump(enrollments, file, indent=4)

def enroll_student(student_id, course_id):

    students = load_students()
    courses = load_courses()
    enrollments = load_enrollments()

    student_exists = any(student["student_id"] == student_id for student in students)
    course_exists = any(course["course_id"] == course_id for course in courses)

    if not student_exists:
        return "Student not found."

    if not course_exists:
        return "Course not found."

    for enrollment in enrollments:
        if enrollment["student_id"] == student_id and enrollment["course_id"] == course_id:
            return "Student is already enrolled."

    enrollments.append({
        "student_id": student_id,
        "course_id": course_id
    })

    
    save_enrollments(enrollments)
    logger.info(f"Student {student_id} enrolled in Course {course_id}")
    return "Enrollment successful."

def view_enrollments():

    students = load_students()
    courses = load_courses()
    enrollments = load_enrollments()

    if not enrollments:
        print("No enrollments found.")
        return

    table = []

    for enrollment in enrollments:

        student_name = ""
        course_name = ""

        for student in students:
            if student["student_id"] == enrollment["student_id"]:
                student_name = student["name"]
                break

        for course in courses:
            if course["course_id"] == enrollment["course_id"]:
                course_name = course["course_name"]
                break

        table.append({
            "Student ID": enrollment["student_id"],
            "Student Name": student_name,
            "Course ID": enrollment["course_id"],
            "Course Name": course_name
        })

    print(tabulate(table, headers="keys", tablefmt="grid"))

    