from inspect import getcallargs
from functools import wraps
from covenant.util import toggled_decorator_func


@toggled_decorator_func
def pre(condition):
    def _pre(func):
        @wraps(func)
        def wrapped_func(*args, **kwargs):
            callargs = getcallargs(func, *args, **kwargs)
            result = condition(**callargs)
            if not result:
                raise AssertionError("Precondition check failed.")

            return func(*args, **kwargs)

        return wrapped_func
    return _pre


@toggled_decorator_func
def post(condition):
    def _post(func):
        @wraps(func)
        def wrapped_func(*args, **kwargs):
            callargs = getcallargs(func, *args, **kwargs)

            value = func(*args, **kwargs)

            result = condition(value, **callargs)

            if not result:
                raise AssertionError("Precondition check failed.")

        return wrapped_func
    return _post
