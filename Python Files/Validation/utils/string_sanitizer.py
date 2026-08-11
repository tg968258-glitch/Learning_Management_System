
def remove_spaces(text: str) -> str:
    """
    Remove leading and trailing whitespace.

    Args:
        text (str): Input string.

    """
    return text.strip()


def to_lowercase(text: str) -> str:
    """
    Convert text to lowercase.

    Args:
        text (str): Input string.

    
    """
    return text.lower()


def to_uppercase(text: str) -> str:
    """
    Convert text to uppercase.

    Args:
        text (str): Input string.

    
    """
    return text.upper()


def capitalize_text(text: str) -> str:
    """
    Capitalize the first letter.

    Args:
        text (str): Input string.

    
    """
    return text.capitalize()



def remove_digits(text: str) -> str:
    """
    Remove all digits from the string.

    Args:
        text (str): Input string.

    
    """
    return "".join(char for char in text if not char.isdigit())


