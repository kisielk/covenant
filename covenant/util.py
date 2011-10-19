from functools import wraps
from covenant.base import is_enabled


def _null_decorator(obj):
    return obj


def toggled_decorator(deco):
    @wraps(deco)
    def _inner(func):
        if is_enabled():
            return deco(func)
        else:
            return func

    return _inner


def toggled_decorator_func(deco):
    @wraps(deco)
    def _inner(*args, **kwargs):
        if is_enabled():
            return deco(*args, **kwargs)
        else:
            return _null_decorator

    return _inner
