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


def post(condition, imports=None):
    """Decorate a function with a post-condition"""
    return __create_deco(condition, "post", imports)


def pre(condition, imports=None):
    """Decorate a function with a pre-condition"""
    return __create_deco(condition, "pre", imports)


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


def check_preconditions(pre, callargs):
    for precondition in pre:
        eval_globals = callargs.copy()
        eval_globals.update(precondition.imports)
        statement = precondition.statement
        try:
            cond_result = eval(statement, eval_globals, None)
        except Exception as e:
            raise PreconditionViolation("Precondition {0} failed with "
                                        "exception {1}".format(statement, e))
        if not cond_result:
            raise PreconditionViolation("Precondition {0} not met."
                                        .format(statement))


def check_postconditions(post, callargs, rval):
    for postcondition in post:
        eval_globals = callargs.copy()
        eval_globals.update(postcondition.imports)
        eval_globals["_c"] = rval
        statement = postcondition.statement
        try:
            cond_result = eval(statement, eval_globals, None)
        except Exception as e:
            raise PostconditionViolation("Postcondition {0} failed with "
                                         "exception {1}".format(statement, e))
        if not cond_result:
            raise PostconditionViolation("Postcondition {0} not met."
                                         .format(statement))


def check_conditions(func, pre, post, args, kwargs):
    callargs = getcallargs(func, *args, **kwargs)
    check_preconditions(pre, callargs)
    rval = func(*args, **kwargs)
    check_postconditions(post, callargs, rval)
    return rval
