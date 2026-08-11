from utils.input_validator import (validate_length)

password = input("Enter password: ")

if validate_length(password, 8, 16):
    print("Password Accepted")
else:
    print("Password must be between 8 and 16 characters.")