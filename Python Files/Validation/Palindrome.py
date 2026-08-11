from utils.numeric_validator import (is_integer)
number = input("Enter a number: ")

if is_integer(number):
    if number == number[::-1]:
        print("Palindrome")
    else:
        print("Not Palindrome")
else:
    print("Invalid Integer")