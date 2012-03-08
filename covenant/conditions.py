from inspect import getcallargs
from functools import wraps

from covenant.util import toggled_decorator_func
from covenant.exceptions import (PreconditionViolationError,
                                 PostconditionViolationError)


@toggled_decorator_func
def pre(condition):
    """Enforce a precondition on the decorated function.

    The `condition` must be a callable that receives the same keyword arguments
    as the function it's being applied to.

    """
    def _pre(func):
        original_func = getattr(func, '_original_func', func)

        @wraps(func)
        def wrapped_func(*args, **kwargs):
            callargs = getcallargs(original_func, *args, **kwargs)

            try:
                result = condition(**callargs)
            except Exception as e:
                # TODO: Better error message including exception
                raise PreconditionViolationError("Precondition check failed.")

            if not result:
                raise PreconditionViolationError("Precondition check failed.")

            return func(*args, **kwargs)

        wrapped_func._original_func = original_func
        return wrapped_func
    return _pre


@toggled_decorator_func
def post(condition):
    """Enforce a postcondition on the decorated function.

    The `condition` must be a callable that receives the return value of the
    function it's being applied to as its first parameter, and the keyword
    arguments of the function it's applied to as its remaining parameters.

    """
    def _post(func):
        original_func = getattr(func, '_original_func', func)

        @wraps(func)
        def wrapped_func(*args, **kwargs):
            callargs = getcallargs(original_func, *args, **kwargs)

            value = func(*args, **kwargs)

            try:
                result = condition(value, **callargs)
            except Exception as e:
                # TODO: Better error message including exception
                raise PostconditionViolationError("Postcondition check failed.")

            if not result:
                raise PostconditionViolationError("Postcondition check failed.")

            return value

        wrapped_func._original_func = original_func
        return wrapped_func
    return _post
