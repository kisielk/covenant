class ContractViolationError(AssertionError):
    """Base class for all covenant contract violations."""
    pass


class PreconditionViolationError(ContractViolationError):
    """Raised when a function precondition is violated."""
    pass


class PostconditionViolationError(ContractViolationError):
    """Raised when a function postcondition is violated."""
    pass


class InvariantViolationError(ContractViolationError):
    """Raised when a class invariant is violated."""
    pass
