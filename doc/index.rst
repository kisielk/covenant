covenant - Code contracts for Python 3
======================================
covenant is a Python 3 library for enforcing code contracts.

.. contents::
    :local:

Preconditions
-------------
Preconditions are checked before a function is called.

Preconditions are applied to a function via the :func:`@pre` decorator. The
decorator takes a single argument: a callable with the same number of parameters
as the function being decorated::

    from covenant import pre

    @pre(lambda x: x < 10)
    def some_function(x):
        ...

If the decorated function may be called with keyword arguments then the names of
the precondition's arguments should match those of the function. When decorating 
a class method, the precondition should include the *self* argument::

    @pre(lambda self, x: x < self.max)
    def some_method(self, x):
        ...

If the value returned by the precondition evalues to *False* or it raises an
Exception then the precondition has been violated and a
:exc:`PreconditionViolationError` will be raised.

Postconditions
--------------
Postconditions are checked after a function is called.

Postconditions are applied to a function via the :func:`@post` decorator. The
decorator takes a single argument: a callable whose first argument is the
function's return value and the remaining arguments match those of the function
being decorated::

    from covenant import post

    @post(lambda r, x: r < x)
    def some_function(x):
        return x - 20

If the value returned by the postcondition evalues to *False* or it raises an
Exception then the precondition has been violated and a
:exc:`PostconditionViolationError` will be raised.

Function Annotations
--------------------

Class Invariants
----------------


