from inspect import getcallargs
from decorator import decorator

from covenant.util import toggled_decorator
from covenant.exceptions import (PreconditionViolationError,
                                 PostconditionViolationError)


@toggled_decorator
@decorator
def constrain(func, *args, **kwargs):
    """Enforce constraints on a function defined by its annotations.

    Each annotation should be a callable that takes a single parameter and
    returns a True or False value.

    """
    callargs = getcallargs(func, *args, **kwargs)

    for arg, arg_value in callargs.items():
        if arg in func.__annotations__:
            try:
                result = func.__annotations__[arg](arg_value)
            except Exception as e:
                raise PreconditionViolationError("{0}: {1}".format(arg_value, e))

            if not result:
                raise PreconditionViolationError(arg_value)

    value = func(*args, **kwargs)

    if "return" in func.__annotations__:
        try:
            result = func.__annotations__["return"](value)
        except Exception as e:
            raise PostconditionViolationError(e)

        if not result:
            raise PostconditionViolationError()

    return value


__all__ = ["constrain"]
