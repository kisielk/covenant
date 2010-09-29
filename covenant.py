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


def pre(condition, imports=None):
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
            # Eval the condition
            if not eval(condition, callargs, None):
                raise PreconditionViolation("Precondition {0} not met.".format(condition))
            # Call the actual function
            return func(*args, **kwargs)
        wrapper._covenant_base_func = base_func
        return wrapper
    return deco

def post(condition, imports=None):
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
            # Call the actual function
            rval = func(*args, **kwargs)
            # Eval the condition
            callargs["_c"] = rval
            if not eval(condition, callargs, None):
                raise PostconditionViolation("Precondition {0} not met.".format(condition))
            else:
                return rval
        wrapper._covenant_base_func = base_func
        return wrapper
    return deco
