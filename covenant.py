
def ContractViolation(Exception):
    pass

def PreconditionViolation(ContractViolationError):
    pass

def PostconditionViolation(ContractViolationError):
    pass

def ClassInvariantViolation(ContractViolationError):
    pass

def pre(args):
    """Precondition decorator generator."""
    def _dec(func):
        return func
    return _dec

def post(func):
    """Postcondition decorator generator."""
    pass

def invariant(func):
    """Class invariant decorator generator."""
    pass

def arg(name):
    """Something something to an arg."""
    pass
