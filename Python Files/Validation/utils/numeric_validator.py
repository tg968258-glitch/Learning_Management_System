
def is_integer(value: int) -> bool:
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


def is_float(value: str) -> bool:
    """
    Check whether the value can be converted to a float.

    Args:
        value (str): Input value.

    """
    try:
        float(value)
        return True
    except ValueError:
        return False


def is_positive(number: int | float) -> bool:
    """
    Check whether a number is positive.

    Args:
        number (int | float): Number.

    
    """
    return number > 0


def is_negative(number: int | float) -> bool:
    """
    Check whether a number is negative.

    Args:
        number (int | float): Number.

    
    """
    return number < 0





def is_even(number: int) -> bool:
    """
    Check whether a number is even.

    Args:
        number (int): Number.

    
    """
    return number % 2 == 0


def is_odd(number: int) -> bool:
    """
    Check whether a number is odd.

    Args:
        number (int): Number.

    
    """
    return number % 2 != 0