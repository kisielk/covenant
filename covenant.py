from inspect import getcallargs
from functools import wraps
from collections import namedtuple

if __debug__:
    __ENABLED = True
else:
    __ENABLED = False


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


class ContractViolationError(Exception):
    pass


class PreconditionViolation(ContractViolationError):
    pass


class PostconditionViolation(ContractViolationError):
    pass


class InvariantViolation(ContractViolationError):
    pass


Condition = namedtuple("Condition", "statement, imports")


def create_wrapper(func, pre=None, post=None):
    """Create a wrapper for func that will check pre and post conditions."""
    if not pre:
        pre = []
    if not post:
        post = []

    @wraps(func)
    def wrapper(*args, **kwargs):
        return check_conditions(func=func, pre=pre, post=post,
                                args=args, kwargs=kwargs)

    wrapper._covenant_pre = pre
    wrapper._covenant_post = post
    wrapper._covenant_base_func = func
    return wrapper


def __null_deco(func):
    """Function decorator that does nothing"""
    return func


def __create_deco(condition, order, imports):
    """Create function decorator for pre or post-conditions.
    order must be either "pre" or "post"
    """
    if not __ENABLED:
        deco = __null_deco
    else:
        if not imports:
            imports = {}

        def deco(func):
            cond = Condition(condition, imports)
            if hasattr(func, "_covenant_base_func"):
                getattr(func, "_covenant_" + order).append(cond)
                return func
            else:
                wrapper_args = {order: [cond], "func": func}
                return create_wrapper(**wrapper_args)

    return deco


def invariant(condition, imports=None):
    """Decorate a class with an invariant.
    The class must be of the InvariantMeta metaclass.
    """
    if not imports:
        imports = {}

    def deco(cls):
        invariant = Condition(condition, imports)
        if not hasattr(cls, "_covenant_invariants"):
            raise TypeError("Class {0} is not using the "
                            "InvariantMeta metaclass")
        else:
            cls._covenant_invariants.append(invariant)
        return cls

    return deco


def bind(func):
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
