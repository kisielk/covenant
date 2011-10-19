from inspect import getcallargs, getargspec, isfunction, getmembers
from functools import wraps
from covenant.util import toggled_decorator_func


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


@toggled_decorator_func
def invariant(condition):
    def _invariant(cls):
        for attr_name, attr in getmembers(cls, isfunction):
            if 'self' in getargspec(attr).args:
                wrapper = _invariant_wrapper(attr, condition)
                setattr(cls, attr_name, wrapper)

        return cls
    return _invariant
