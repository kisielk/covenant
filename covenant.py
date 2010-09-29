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

def invariant(func):
    """Class invariant decorator generator."""
    pass

def post(check, imports=None):
    """Postcondition decorator generator."""
    if not imports:
        imports = {}
    def deco(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return deco

def pre(check, imports=None):
    if not imports:
        imports = {}
    def deco(func):
        if hasattr(func, "_covenant_base_func"):
            base_func = func._covenant_base_func
        else:
            base_func = func
        @wraps(func)
        def wrapper(*args, **kwargs):
            callargs = {}
            spec = inspect.getargspec(base_func)
            # Set defaults
            if spec.defaults:
                for arg, default in itertools.izip(reversed(spec.args), 
                                                reversed(spec.defaults)):
                    callargs[arg] = default
            # Populate from passed args
            for a1, a2 in itertools.izip(spec.args, args):
                callargs[a1] = a2
            # Update with kwargs and provided imports
            callargs.update(kwargs)
            callargs.update(imports)
            # Eval the check
            if not eval(check, callargs, None):
                raise PreconditionViolation("Precondition {0} not met.".format(check))
            # Call the actual function
            return func(*args, **kwargs)
        wrapper._covenant_base_func = base_func
        return wrapper
    return deco
