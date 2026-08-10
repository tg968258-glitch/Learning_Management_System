import re

def is_empty(value) -> bool:
    """
    Check whether the given string is empty.

    Args:
        value : Input string.

    """
    return value.strip() == ""


def validate_length(text: str, min_length = 1, max_length = 100) -> bool:
    """
    Check whether the text length is within the specified range.

    Args:
        text (str): Input string.
        min_length (int): Minimum allowed length.
        max_length (int): Maximum allowed length.

    """
    return min_length <= len(text) <= max_length


def is_alpha(text: str) -> bool:
    """
    Check whether the string contains only alphabetic characters.

    Args:
        text (str): Input string.

    
    """
    return (text.strip()and all(ch.isalpha() or ch.isspace() for ch in text))


def is_valid_email(value):
    """
    Validate email format.
    """
    pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    return re.fullmatch(pattern, value) is not None


def is_unique(value, records, key):
      """
    Check whether value already exists.
    """
      return all(record[key] != value for record in records)

def is_valid_choice(choice, minimum, maximum):
    """
    Validate CLI menu choice.
    """
    try:
        choice = int(choice)
        return minimum <= choice <= maximum
    except ValueError:
        return False