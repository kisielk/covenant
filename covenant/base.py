if __debug__:
    _ENABLED = True
else:
    _ENABLED = False


def disable():
    """Disable covenant functionality"""
    global _ENABLED
    _ENABLED = False


def enable():
    """Enable covenant functionality"""
    global _ENABLED
    _ENABLED = True


def is_enabled():
    """Returns True if covenant functionality is enabled"""
    return _ENABLED
