from inspect import getcallargs
from functools import wraps

from covenant.util import toggled_decorator
from covenant.exceptions import (PreconditionViolationError,
                                 PostconditionViolationError)


@toggled_decorator
def constrain(func):
    """Enforce constraints on a function defined by its annotations.

    Each annotation should be a callable that takes a single parameter and
    returns a True or False value.

    """
    @wraps(func)
    def wrapped_func(*args, **kwargs):
        callargs = getcallargs(func, *args, **kwargs)
        for arg, arg_value in callargs.items():
            if arg in func.__annotations__:
                result = func.__annotations__[arg](arg_value)
                if not result:
                    raise PreconditionViolationError(
                        "Precondition check failed: {0}".format(arg_value))

        value = func(*args, **kwargs)

        if "return" in func.__annotations__:
            result = func.__annotations__["return"](value)
            if not result:
                raise PostconditionViolationError(
                    "Postcondtion check failed: {0}" .format(value))

        return value

    return wrapped_func
