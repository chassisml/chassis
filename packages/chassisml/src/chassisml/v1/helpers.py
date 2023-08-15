import warnings
import inspect
from typing import Optional

warnings.filterwarnings("default", category=DeprecationWarning)


def deprecated(message: Optional[str] = None):
    caller = caller_name()
    msg = f"'{caller}' will change or be removed in the next release."
    if message is not None:
        msg += " " + message
    warnings.warn(msg, DeprecationWarning, stacklevel=3)


# https://stackoverflow.com/a/9812105
def caller_name(skip=2):
    """
    Get a name of a caller in the format module.class.method

    `skip` specifies how many levels of stack to skip while getting caller
    name. skip=1 means "who calls me", skip=2 "who calls my caller" etc.

    An empty string is returned if skipped levels exceed stack height
    """
    stack = inspect.stack()
    start = 0 + skip
    if len(stack) < start + 1:
        return ''
    parentframe = stack[start][0]

    name = []
    module = inspect.getmodule(parentframe)
    # `module` can be None when frame is executed directly in console
    if module:
        name.append(module.__name__)
    # detect classname
    if 'self' in parentframe.f_locals:
        # I don't know any way to detect call from the object method
        # XXX: there seems to be no way to detect static method call - it will
        #      be just a function call
        name.append(parentframe.f_locals['self'].__class__.__name__)
    codename = parentframe.f_code.co_name
    if codename not in ['<module>', "__init__"]:  # top level usually
        name.append(codename)  # function or a method

    # Avoid circular refs and frame leaks
    # https://docs.python.org/2.7/library/inspect.html#the-interpreter-stack
    del parentframe, stack

    return ".".join(name)
