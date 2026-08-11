

def is_empty(value: str) -> bool:
    """
    Check whether the given string is empty.

    Args:
        value (str): Input string.

    """
    return value.strip() == ""


def validate_length(text: str, min_length: int = 1, max_length: int = 100) -> bool:
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
    return text.isalpha()


def is_alphanumeric(text: str) -> bool:
    """
    Check whether the string contains only letters and digits.

    Args:
        text (str): Input string.

    
    """
    return text.isalnum()