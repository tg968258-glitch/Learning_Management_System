from services.filehandler import *
from utils.input_validator import *
from utils.numeric_validator import *
from utils.string_sanitizer import *
import questionary


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def prompt_required_text(label, allow_spaces_ok=False):
   
    while True:
        raw = input(f"Enter {label}: ")
        cleaned = capitalize_text(remove_spaces(raw))

        if is_empty(cleaned):
            print(f"Invalid {label}! {label} cannot be empty.")
            continue

        if not is_alpha(cleaned):
            print(f"Invalid {label}! Please enter alphabets only.")
            continue

        return cleaned


def prompt_update_text(label, current_value):
 
    while True:
        raw = input(f"Enter New {label} [{current_value}] (press Enter to keep current): ")

        if raw.strip() == "":
            return current_value

        cleaned = capitalize_text(remove_spaces(raw))

        if is_empty(cleaned):
            print(f"Invalid {label}! {label} cannot be empty.")
            continue

        if not is_alpha(cleaned):
            print(f"Invalid {label}! Please enter alphabets only.")
            continue

        return cleaned


def prompt_update_generic(label, current_value, validator_fn, error_msg, cast_fn=None):
    
    while True:
        raw = input(f"Enter New {label} [{current_value}] (press Enter to keep current): ")

        if raw.strip() == "":
            return current_value

        if validator_fn(raw):
            return cast_fn(raw) if cast_fn else raw

        print(f"Invalid {label}! {error_msg}")


def select_gender(current=None):
   

    keep_label = f"Keep current ({current})" if current else None
    choices = [keep_label] if keep_label else []
    choices += ["M", "F", "O"]

    result = questionary.select("Select Gender (M/F/O):", choices=choices).ask()

    if keep_label and result == keep_label:
        return current

    return result


def confirm_action(prompt_text):
    
    while True:
        answer = input(f"{prompt_text} (y/n): ").strip().lower()

        if answer == "y":
            return True
        elif answer == "n":
            return False

        print("Invalid input! Please enter 'y' or 'n'.")


def print_student(student):
    print("----------------------------------")
    print(f"Student ID : {student['student_id']}")
    print(f"Name       : {student['name']}")
    print(f"Age        : {student['age']}")
    print(f"Gender     : {student['gender']}")
    print(f"Email      : {student['email']}")
    print(f"Phone      : {student['phone_number']}")
    print(f"Percentage : {student['percentage']}")
    print("----------------------------------")


def print_course(course):
    print("----------------------------------")
    print(f"Course ID   : {course['course_id']}")
    print(f"Course Name : {course['course_name']}")
    print(f"Trainer     : {course['trainer']}")
    print(f"Duration    : {course['duration']}")
    print("----------------------------------")


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

while True:

    print("\n========== LEARNING MANAGEMENT SYSTEM ==========")

    choice = questionary.select(
        "Learning Management System",
        choices=[
            "1. Add Student",
            "2. View Students",
            "3. Update Student",
            "4. Delete Student",
            "5. Search Student",
            questionary.Separator(),

            "6. Add Course",
            "7. View Courses",
            "8. Update Course",
            "9. Delete Course",
            "10. Search Course",
            questionary.Separator(),

            "11. Enroll Student",
            "12. View Enrollments",
            questionary.Separator(),

            "13. Exit"
        ]
    ).ask()
    choice = int(choice.split(".")[0])

    # ---------------- ADD STUDENT ----------------
    if choice == 1:

        student_id = generate_student_id()
        print(f"Generated Student ID: {student_id}")

        # Name
        name = prompt_required_text("Name")

        # Age
        while True:
            age = input("Enter Age: ")

            if is_empty(age):
                print("Invalid Age! Age cannot be empty.")
                continue

            if is_integer(age):
                age = int(age)
                break

            print("Invalid Age! Please enter a valid integer.")

        # Gender
        gender = select_gender()

        # Email
        while True:
            email = to_lowercase(remove_spaces(input("Enter Email: ")))

            if is_empty(email):
                print("Invalid Email! Email cannot be empty.")
                continue

            if is_valid_email(email):
                break

            print("Invalid Email! Please enter a valid email address in Format: username@example.com")

        # Phone Number
        while True:
            phone = input("Enter Phone Number: ")

            if is_empty(phone):
                print("Invalid Phone Number! Phone number cannot be empty.")
                continue

            if is_phone_number(phone):
                break

            print("Invalid Phone Number! Enter 10 numeric digits only from 0 to 9")

        # Percentage
        while True:
            percentage = input("Enter Percentage: ")

            if is_empty(percentage):
                print("Invalid Percentage! Percentage cannot be empty.")
                continue

            if is_float(percentage) and in_range(percentage, 0, 100):
                percentage = float(percentage)
                break

            print("Invalid Percentage! Enter a numeric value between 0 and 100.")

        student = {
            "student_id": student_id,
            "name": name,
            "age": age,
            "gender": gender,
            "email": email,
            "phone_number": phone,
            "percentage": percentage
        }

        add_student(student)
        print("Student added successfully.")

    # ---------------- VIEW STUDENT ----------------
    elif choice == 2:

        view_students()

    # ---------------- UPDATE STUDENT ----------------
    elif choice == 3:

        # Student ID
        while True:
            student_id = input("Enter Student ID to update: ")

            if not is_integer(student_id):
                print("Invalid Student ID! Please enter a valid integer.")
                continue

            student_id = int(student_id)
            student = search_student(student_id)

            if student:
                break

            print("Student not found.")

        print("\nCurrent Details")
        print_student(student)
        print("Press Enter on any field to keep its current value.\n")

        # Name
        name = prompt_update_text("Name", student["name"])

        # Age
        while True:
            raw_age = input(f"Enter New Age [{student['age']}] (press Enter to keep current): ")

            if raw_age.strip() == "":
                age = student["age"]
                break

            if is_integer(raw_age) and is_positive(raw_age):
                age = int(raw_age)
                break

            print("Invalid Age! Please enter a positive integer.")

        # Gender
        gender = select_gender(current=student["gender"])

        # Email
        while True:
            raw_email = input(f"Enter New Email [{student['email']}] (press Enter to keep current): ")

            if raw_email.strip() == "":
                email = student["email"]
                break

            email_candidate = to_lowercase(remove_spaces(raw_email))

            if is_valid_email(email_candidate):
                email = email_candidate
                break

            print("Invalid Email! Please enter a valid email address in Format: username@example.com")

        # Phone
        while True:
            raw_phone = input(f"Enter New Phone Number [{student['phone_number']}] (press Enter to keep current): ")

            if raw_phone.strip() == "":
                phone = student["phone_number"]
                break

            if is_phone_number(raw_phone):
                phone = raw_phone
                break

            print("Invalid Phone Number! Enter 10 digits from 0 to 9.")

        # Percentage
        while True:
            raw_percentage = input(
                f"Enter New Percentage [{student['percentage']}] (press Enter to keep current): "
            )

            if raw_percentage.strip() == "":
                percentage = student["percentage"]
                break

            if is_float(raw_percentage) and in_range(raw_percentage, 0, 100):
                percentage = float(raw_percentage)
                break

            print("Invalid Percentage! Enter a numeric value between 0 and 100.")

        updated_data = {
            "name": name,
            "age": age,
            "gender": gender,
            "email": email,
            "phone_number": phone,
            "percentage": percentage
        }

        update_student(student_id, updated_data)
        print("Student updated successfully.")

    # ---------------- DELETE STUDENT ----------------
    elif choice == 4:

        while True:
            student_id = input("Enter Student ID to delete: ")

            if is_integer(student_id):
                student_id = int(student_id)
                break

            print("Invalid Student ID! Please enter a valid integer.")

        student = search_student(student_id)

        if not student:
            print("Student not found.")
        else:
            print("\nStudent to delete:")
            print_student(student)

            if confirm_action("Are you sure you want to delete this student?"):
                if delete_student(student_id):
                    print("Student deleted successfully.")
                else:
                    print("Student not found.")
            else:
                print("Student not deleted.")

    # ---------------- SEARCH STUDENT ----------------
    elif choice == 5:

        while True:
            student_id = input("Enter Student ID: ")

            if is_integer(student_id):
                student_id = int(student_id)
                break

            print("Invalid Student ID! Please enter a valid integer.")

        student = search_student(student_id)

        if student:
            print("\n========== STUDENT FOUND ==========")
            print_student(student)
        else:
            print("Student not found.")

    # ---------------- ADD COURSE ----------------
    elif choice == 6:

        course_id = generate_course_id()
        print(f"Generated Course ID: {course_id}")

        # Course Name
        while True:
            course_name = capitalize_text(remove_spaces(input("Enter Course Name: ")))

            if is_empty(course_name):
                print("Invalid Course Name! Course Name cannot be empty.")
                continue

            if is_alpha(course_name) and validate_length(course_name):
                break

            print("Invalid Course Name! Enter alphabets only.")

        # Trainer Name
        while True:
            trainer = capitalize_text(remove_spaces(input("Enter Trainer Name: ")))

            if is_empty(trainer):
                print("Invalid Trainer Name! Trainer Name cannot be empty.")
                continue

            if is_alpha(trainer) and validate_length(trainer):
                break

            print("Invalid Trainer Name! Enter alphabets only.")

        # Duration
        while True:
            duration = input("Enter Duration (Days): ")

            if is_empty(duration):
                print("Invalid Duration! Duration cannot be empty.")
                continue

            if is_integer(duration) and is_positive(duration):
                duration = f"{duration} Days"
                break

            print("Invalid Duration! Enter a positive number.")

        course = {
            "course_id": course_id,
            "course_name": course_name,
            "trainer": trainer,
            "duration": duration
        }

        add_course(course)
        print("Course added successfully.")

    # ---------------- VIEW COURSES ----------------
    elif choice == 7:

        view_courses()

    # ---------------- UPDATE COURSE ----------------
    elif choice == 8:

        # Course ID
        while True:
            course_id = input("Enter Course ID to update: ")

            if not is_integer(course_id):
                print("Invalid Course ID! Enter valid numeric course ID")
                continue

            course_id = int(course_id)
            course = search_course(course_id)

            if course:
                break

            print("Course not found.")

        print("\nCurrent Details")
        print_course(course)
        print("Press Enter on any field to keep its current value.\n")

        # Course Name
        while True:
            raw_name = input(
                f"Enter New Course Name [{course['course_name']}] (press Enter to keep current): "
            )

            if raw_name.strip() == "":
                course_name = course["course_name"]
                break

            candidate = capitalize_text(remove_spaces(raw_name))

            if is_empty(candidate):
                print("Invalid Course Name! Course Name cannot be empty.")
                continue

            if is_alpha(candidate) and validate_length(candidate):
                course_name = candidate
                break

            print("Invalid Course Name! Please enter alphabets and spaces only")

        # Trainer Name
        while True:
            raw_trainer = input(
                f"Enter New Trainer Name [{course['trainer']}] (press Enter to keep current): "
            )

            if raw_trainer.strip() == "":
                trainer = course["trainer"]
                break

            candidate = capitalize_text(remove_spaces(raw_trainer))

            if is_empty(candidate):
                print("Invalid Trainer Name! Trainer Name cannot be empty.")
                continue

            if is_alpha(candidate) and validate_length(candidate):
                trainer = candidate
                break

            print("Invalid Trainer Name! Please enter alphabets and spaces only")

        # Duration
        while True:
            raw_duration = input(
                f"Enter New Duration (Days) [{course['duration']}] (press Enter to keep current): "
            )

            if raw_duration.strip() == "":
                duration = course["duration"]
                break

            if is_integer(raw_duration) and is_positive(raw_duration):
                duration = f"{raw_duration} Days"
                break

            print("Invalid Duration! Enter a positive number.")

        updated_data = {
            "course_name": course_name,
            "trainer": trainer,
            "duration": duration
        }

        update_course(course_id, updated_data)
        print("Course updated successfully.")

    # ---------------- DELETE COURSE ----------------
    elif choice == 9:

        while True:
            course_id = input("Enter Course ID to delete: ")

            if is_integer(course_id):
                course_id = int(course_id)
                break

            print("Invalid Course ID! Enter valid numeric course ID")

        course = search_course(course_id)

        if not course:
            print("Course not found.")
        else:
            print("\nCourse to delete:")
            print_course(course)

            if confirm_action("Are you sure you want to delete this course?"):
                if delete_course(course_id):
                    print("Course deleted successfully.")
                else:
                    print("Course not found.")
            else:
                print("Course not deleted.")

    # ---------------- SEARCH COURSE ----------------
    elif choice == 10:

        while True:
            course_id = input("Enter Course ID: ")

            if is_integer(course_id):
                course_id = int(course_id)
                break

            print("Invalid Course ID! Enter valid numeric course ID")

        course = search_course(course_id)

        if course:
            print("\n========== COURSE FOUND ==========")
            print_course(course)
        else:
            print("Course not found.")

    # ---------------- ENROLL STUDENT ----------------
    elif choice == 11:

        # Student ID
        while True:
            student_id = input("Enter Student ID: ")

            if is_integer(student_id):
                student_id = int(student_id)

                if search_student(student_id):
                    break

                print("Student ID does not exist.")
            else:
                print("Invalid Student ID! Please enter a valid integer.")

        # Course ID
        while True:
            course_id = input("Enter Course ID: ")

            if is_integer(course_id):
                course_id = int(course_id)

                if search_course(course_id):
                    break

                print("Course ID does not exist.")
            else:
                print("Invalid Course ID! Please enter a valid integer.")

        message = enroll_student(student_id, course_id)
        print(message)

    # ---------------- VIEW ENROLLMENTS ----------------
    elif choice == 12:

        view_enrollments()

    # ---------------- EXIT ----------------
    elif choice == 13:

        print("\n========================================")
        print(" Thank you for using Learning Management System ")
        print("========================================")
        break