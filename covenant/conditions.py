from inspect import getcallargs
from decorator import decorator

from covenant.util import toggled_decorator_func
from covenant.exceptions import (PreconditionViolationError,
                                 PostconditionViolationError)


@toggled_decorator_func
def pre(condition):
    """Enforce a precondition on the decorated function.

    The `condition` must be a callable that receives the same keyword arguments
    as the function it's being applied to.

    """
    @decorator
    def _pre(func, *args, **kwargs):
        callargs = getcallargs(func, *args, **kwargs)

        try:
            result = condition(**callargs)
        except Exception as e:
            # TODO: Better error message including exception
            raise PreconditionViolationError("Precondition check failed: %s" % e)

        if not result:
            raise PreconditionViolationError("Precondition check failed.")

        return func(*args, **kwargs)
    return _pre


@toggled_decorator_func
def post(condition):
    """Enforce a postcondition on the decorated function.

    The `condition` must be a callable that receives the return value of the
    function it's being applied to as its first parameter, and the keyword
    arguments of the function it's applied to as its remaining parameters.

    """
    @decorator
    def _post(func, *args, **kwargs):
        callargs = getcallargs(func, *args, **kwargs)

        value = func(*args, **kwargs)

        try:
            result = condition(value, **callargs)
        except Exception as e:
            # TODO: Better error message including exception
            raise PostconditionViolationError("Postcondition check failed: %s" % e)

        if not result:
            raise PostconditionViolationError("Postcondition check failed.")

        return value
    return _post

__all__ = ["pre", "post"]
