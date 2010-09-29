import inspect
from functools import wraps
import itertools

class ContractViolationError(Exception):
    pass

class PreconditionViolation(ContractViolationError):
    pass

class PostconditionViolation(ContractViolationError):
    pass

class ClassInvariantViolation(ContractViolationError):
    pass

def post(func):
    """Postcondition decorator generator."""
    pass

def invariant(func):
    """Class invariant decorator generator."""
    pass

def pre(check):
    def deco(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if hasattr(func, "_covenant_base_func"):
                spec = inspect.getargspec(func._covenant_base_func)
            else:
                spec = inspect.getargspec(func)

            callargs = {}
            # Set defaults
            if spec.defaults:
                for arg, default in itertools.izip(reversed(spec.args), 
                                                reversed(spec.defaults)):
                    callargs[arg] = default
            # Populate from passed args
            for a1, a2 in itertools.izip(spec.args, args):
                callargs[a1] = a2
            # Update with kwargs
            callargs.update(kwargs)
            # Eval the check
            if not eval(check, None, callargs):
                raise PreconditionViolation("Precondition {0} not met.".format(check))
            # Call the actual function
            return func(*args, **kwargs)
        wrapper._covenant_base_func = func
        return wrapper
    return deco
