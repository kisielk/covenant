from inspect import getcallargs, getargspec, isfunction, getmembers
from functools import wraps

if __debug__:
    __ENABLED = True
else:
    __ENABLED = False


# Keep track of which invariant checks are currently happening so that
# we don't end up with recursive check issues.
__INVARIANTS_IN_PROGRESS = set()


def __invariant_decorator(condition):
    def _invariant(cls):
        for attr_name, attr in getmembers(cls, isfunction):
            if 'self' in getargspec(attr).args:
                wrapper = __invariant_wrapper(attr, condition)
                setattr(cls, attr_name, wrapper)

        return cls
    return _invariant


def __invariant_wrapper(attr, condition):
    @wraps(attr)
    def wrapper(*args, **kwargs):
        callargs = getcallargs(attr, *args, **kwargs)
        inst = callargs['self']

        value = attr(*args, **kwargs)

        inst_id = id(inst)
        if not inst_id in __INVARIANTS_IN_PROGRESS:
            __INVARIANTS_IN_PROGRESS.add(inst_id)
            result = condition(inst)
            __INVARIANTS_IN_PROGRESS.remove(inst_id)
            print("Result: {0}".format(result))
            if not result:
                raise AssertionError("Invariant violated.")

        return value

    return wrapper


def __bind_wrapper(func):
    @wraps(func)
    def bound_func(*args, **kwargs):
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

    return bound_func


def invariant(condition):
    """Decorate a class with an invariant.
    The class must be of the InvariantMeta metaclass.
    """
    if is_enabled():
        return __invariant_decorator(condition)
    else:
        def null_decorator(cls):
            return cls
        return null_decorator


def bind(func):
    if is_enabled:
        return __bind_wrapper(func)
    else:
        return func


def disable():
    """Disable covenant functionality"""
    global __ENABLED
    __ENABLED = False


def enable():
    """Enable covenant functionality"""
    global __ENABLED
    __ENABLED = True


def is_enabled():
    """Returns True if covenant functionality is enabled"""
    return __ENABLED
