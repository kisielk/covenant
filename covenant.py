from inspect import getcallargs, getargspec, isfunction, getmembers
from functools import wraps


if __debug__:
    _ENABLED = True
else:
    _ENABLED = False


def disable():
    """Disable covenant functionality"""
    global _ENABLED
    _ENABLED = False


def enable():
    """Enable covenant functionality"""
    global _ENABLED
    _ENABLED = True


def is_enabled():
    """Returns True if covenant functionality is enabled"""
    return _ENABLED


# Keep track of which invariant checks are currently happening so that
# we don't end up with recursive check issues.
_INVARIANTS_IN_PROGRESS = set()


def _invariant_wrapper(attr, condition):
    @wraps(attr)
    def wrapper(*args, **kwargs):
        callargs = getcallargs(attr, *args, **kwargs)
        inst = callargs['self']

        value = attr(*args, **kwargs)

        inst_id = id(inst)
        if not inst_id in _INVARIANTS_IN_PROGRESS:
            _INVARIANTS_IN_PROGRESS.add(inst_id)
            result = condition(inst)
            _INVARIANTS_IN_PROGRESS.remove(inst_id)
            if not result:
                raise AssertionError("Invariant violated.")

        return value

    return wrapper


def _null_decorator(obj):
    return obj


def _decorate_if_enabled(decorator=True):
    def _inner(func):
        if is_enabled():
            return func
        else:
            return _null_decorator if decorator else func
    return _inner


@_decorate_if_enabled()
def invariant(condition):
    def _invariant(cls):
        for attr_name, attr in getmembers(cls, isfunction):
            if 'self' in getargspec(attr).args:
                wrapper = _invariant_wrapper(attr, condition)
                setattr(cls, attr_name, wrapper)

        return cls
    return _invariant


@_decorate_if_enabled()
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


@_decorate_if_enabled()
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


@_decorate_if_enabled(decorator=False)
def constrain(func):
    @wraps(func)
    def wrapped_func(*args, **kwargs):
        callargs = getcallargs(func, *args, **kwargs)
        for arg, arg_value in callargs.items():
            if arg in func.__annotations__:
                result = func.__annotations__[arg](arg_value)
                if not result:
                    raise AssertionError("Precondition check failed: {0}"
                                            .format(arg_value))

        value = func(*args, **kwargs)

        if "return" in func.__annotations__:
            result = func.__annotations__["return"](value)
            if not result:
                raise AssertionError("Postcondtion check failed: {0}"
                                     .format(value))

        return value

    return wrapped_func
