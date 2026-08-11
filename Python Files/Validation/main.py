from utils.input_validator import (
    is_empty,
    validate_length,
    is_alpha,
    is_alphanumeric,
)

from utils.numeric_validator import (
    is_integer,
    is_float,
    is_positive,
    is_negative,
    is_even,
    is_odd,
)

from utils.string_sanitizer import (
    remove_spaces,
    to_lowercase,
    to_uppercase,
    capitalize_text,
    remove_digits,
    
)


def main():
    print("===== INPUT VALIDATOR =====")

    text = input("Enter a string: ")

    print("Empty:", is_empty(text))
    print("Only alphabets:", is_alpha(text))
    print("Alphanumeric:", is_alphanumeric(text))
    print("Valid length (1-100):", validate_length(text))

    print("\n===== NUMERIC VALIDATOR =====")

    value = input("Enter a number: ")

    if is_integer(value):
        number = int(value)
        print("Integer:", True)
        print("Positive:", is_positive(number))
        print("Negative:", is_negative(number))
        print("Even:", is_even(number))
        print("Odd:", is_odd(number))
        

    elif is_float(value):
        number = float(value)
        print("Float:", True)
        print("Positive:", is_positive(number))
        print("Negative:", is_negative(number))

    else:
        print("Invalid numeric input")

    print("\n===== STRING SANITIZER =====")

    sentence = input("Enter a sentence: ")

    print("Trimmed:", remove_spaces(sentence))
    print("Lowercase:", to_lowercase(sentence))
    print("Uppercase:", to_uppercase(sentence))
    print("Capitalized:", capitalize_text(sentence))
    print("Without Digits:", remove_digits(sentence))
   


if __name__ == "__main__":
    main()