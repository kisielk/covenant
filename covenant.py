from inspect import getargspec, ismethod
from functools import wraps
from collections import namedtuple
import sys

if __debug__:
    __ENABLED = True
else:
    __ENABLED = False

def disable():
    """Disable covenant functionality"""
    __ENABLED = False

def enable():
    """Enable covenant functionality"""
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

# Note: Taken from Python 2.7's inspect.py
def getcallargs(func, *positional, **named):
    """Get the mapping of arguments to values.

    A dict is returned, with keys the function argument names (including the
    names of the * and ** arguments, if any), and values the respective bound
    values from 'positional' and 'named'."""
    args, varargs, varkw, defaults = getargspec(func)
    f_name = func.__name__
    arg2value = {}

    # The following closures are basically because of tuple parameter unpacking.
    assigned_tuple_params = []
    def assign(arg, value):
        if isinstance(arg, str):
            arg2value[arg] = value
        else:
            assigned_tuple_params.append(arg)
            value = iter(value)
            for i, subarg in enumerate(arg):
                try:
                    subvalue = next(value)
                except StopIteration:
                    raise ValueError('need more than %d %s to unpack' %
                                     (i, 'values' if i > 1 else 'value'))
                assign(subarg,subvalue)
            try:
                next(value)
            except StopIteration:
                pass
            else:
                raise ValueError('too many values to unpack')
    def is_assigned(arg):
        if isinstance(arg,str):
            return arg in arg2value
        return arg in assigned_tuple_params
    if ismethod(func) and func.im_self is not None:
        # implicit 'self' (or 'cls' for classmethods) argument
        positional = (func.im_self,) + positional
    num_pos = len(positional)
    num_total = num_pos + len(named)
    num_args = len(args)
    num_defaults = len(defaults) if defaults else 0
    for arg, value in zip(args, positional):
        assign(arg, value)
    if varargs:
        if num_pos > num_args:
            assign(varargs, positional[-(num_pos-num_args):])
        else:
            assign(varargs, ())
    elif 0 < num_args < num_pos:
        raise TypeError('%s() takes %s %d %s (%d given)' % (
            f_name, 'at most' if defaults else 'exactly', num_args,
            'arguments' if num_args > 1 else 'argument', num_total))
    elif num_args == 0 and num_total:
        raise TypeError('%s() takes no arguments (%d given)' %
                        (f_name, num_total))
    for arg in args:
        if isinstance(arg, str) and arg in named:
            if is_assigned(arg):
                raise TypeError("%s() got multiple values for keyword "
                                "argument '%s'" % (f_name, arg))
            else:
                assign(arg, named.pop(arg))
    if defaults:    # fill in any missing values with the defaults
        for arg, value in zip(args[-num_defaults:], defaults):
            if not is_assigned(arg):
                assign(arg, value)
    if varkw:
        assign(varkw, named)
    elif named:
        unexpected = next(iter(named))
        if isinstance(unexpected, unicode):
            unexpected = unexpected.encode(sys.getdefaultencoding(), 'replace')
        raise TypeError("%s() got an unexpected keyword argument '%s'" %
                        (f_name, unexpected))
    unassigned = num_args - len([arg for arg in args if is_assigned(arg)])
    if unassigned:
        num_required = num_args - num_defaults
        raise TypeError('%s() takes %s %d %s (%d given)' % (
            f_name, 'at least' if defaults else 'exactly', num_required,
            'arguments' if num_required > 1 else 'argument', num_total))
    return arg2value

Condition = namedtuple("Condition", "statement, imports")

def create_wrapper(func, pre=None, post=None):
    """Create a wrapper for func that will check the conditions given in pre and post."""
    if not pre:
        pre = []
    if not post:
        post = []
    @wraps(func)
    def wrapper(*args, **kwargs):
        return check_conditions(func=func, pre=pre, post=post, args=args, kwargs=kwargs)
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
                wrapper_args = { order : [cond], "func" : func }
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
            raise TypeError("Class {0} is not using the InvariantMeta metaclass")
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
        except Exception, e:
            raise PreconditionViolation("Precondition {0} failed with exception {1}".format(statement, e))
        if not cond_result:
            raise PreconditionViolation("Precondition {0} not met.".format(statement))

def check_postconditions(post, callargs, rval):
    for postcondition in post:
        eval_globals = callargs.copy()
        eval_globals.update(postcondition.imports)
        eval_globals["_c"] = rval
        statement = postcondition.statement
        try:
            cond_result = eval(statement, eval_globals, None)
        except Exception, e:
            raise PostconditionViolation("Postcondition {0} failed with exception {1}".format(statement, e))
        if not cond_result:
            raise PostconditionViolation("Postcondition {0} not met.".format(statement))

def check_conditions(func, pre, post, args, kwargs):
    callargs = getcallargs(func, *args, **kwargs)
    check_preconditions(pre, callargs)
    rval = func(*args, **kwargs)
    check_postconditions(post, callargs, rval)
    return rval
