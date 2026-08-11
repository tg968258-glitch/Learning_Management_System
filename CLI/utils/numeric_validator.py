
def is_integer(value):
    """
    Check whether the value can be converted to an integer.

    Args:
        value (str): Input value.

    """
    try:
        int(value)
        return True
    except ValueError:
        return False


def is_float(value):
    """
    Check whether the value is float.

    Args:
        value : Float value.

    """
    try:
        float(value)
        return True
    except ValueError:
        return False


def is_positive(value):
    """
    Check whether value is positive

    """
    try: 
        return float(value) > 0
    except ValueError:
        return False
    

def in_range(value, minimum, maximum):
    """
    Check whether value lies within the given range.
    """
    try:
        value = float(value)
        return minimum <= value <= maximum
    except ValueError:
        return False


def is_phone_number(value, length=10):
    """
    Validate numeric phone number.
    
    """
    return value.isdigit() and len(value) == length













