from inspect import getcallargs, getargspec, isfunction, getmembers
from functools import wraps

from covenant.util import toggled_decorator_func
from covenant.exceptions import InvariantViolationError


# Keep track of which invariant checks are currently happening so that
# we don't end up with recursive check issues.
_INVARIANTS_IN_PROGRESS = set()


def _check_invariant(obj, condition):
    obj_id = id(obj)
    if not obj_id in _INVARIANTS_IN_PROGRESS:
        _INVARIANTS_IN_PROGRESS.add(obj_id)
        result = condition(obj)
        _INVARIANTS_IN_PROGRESS.remove(obj_id)
        if not result:
            raise InvariantViolationError("Invariant violated.")



def _invariant_wrapper(attr, condition):
    @wraps(attr)
    def wrapper(*args, **kwargs):
        callargs = getcallargs(attr, *args, **kwargs)
        inst = callargs['self']

        _check_invariant(inst, condition)
        value = attr(*args, **kwargs)
        _check_invariant(inst, condition)

        return value

    return wrapper


@toggled_decorator_func
def invariant(condition):
    """Enforce a class invariant on the decorated class.

    The `condition` must be a callable that takes a class instance as its
    parameter.

    The invariant will be checked once before an instance method of the class
    is called and once after. The invariant is *not* checked multiple times
    within a single call (eg: if the method calls another method).

    """
    def _invariant(cls):
        for attr_name, attr in getmembers(cls, isfunction):
            if 'self' in getargspec(attr).args:
                wrapper = _invariant_wrapper(attr, condition)
                setattr(cls, attr_name, wrapper)

        return cls
    return _invariant

__all__ = ["invariant"]
