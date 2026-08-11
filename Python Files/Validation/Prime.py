from utils.numeric_validator import (is_integer)
number = input("Enter a number: ")

if is_integer(number):
    number = int(number)

    if number < 2:
        print("Not Prime")
    else:
        for val in range(2, int(number ** 0.5) + 1):
            if number % val == 0:
                print("Not Prime")
                break
        else:
            print("Prime")
else:
    print("Invalid Integer")