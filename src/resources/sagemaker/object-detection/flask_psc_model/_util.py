import collections
import os


def is_scalar(obj, force=(bytes, str, collections.Mapping)):
    """Returns True if the object is not iterable or is an instance of one of the forced types."""
    if isinstance(obj, force):
        return True
    try:
        iter(obj)
        return False
    except TypeError:
        return True


def listify(obj, force=(bytes, str, collections.Mapping)):
    """Convert any iterable except types specified in `force` to a new list, otherwise to a single element list."""
    if is_scalar(obj, force=force):
        return [obj]
    return list(obj)


def filepaths_are_equivalent(fp1, fp2):
    """Checks if two filepaths are equivalent. Considers symbolic links."""
    return os.path.normcase(os.path.realpath(fp1)) == os.path.normcase(os.path.realpath(fp2))


def stripext(path):
    """Strip a file extension from a filepath if it exists."""
    return os.path.splitext(path)[0]


def classname(o, prepend_module=True):
    """Attempt to get the qualified name of the Python class/function.

    Includes module name if available unless `prepend_module` is set to false.
    """

    if hasattr(o, '__qualname__'):
        clazz = o
    else:
        clazz = type(o)

    qualname = getattr(clazz, '__qualname__')
    if qualname is None:
        return '<unknown>'

    if not prepend_module:
        return qualname

    module = getattr(clazz, '__module__')
    if module is None or module == str.__class__.__module__:
        return qualname  # Avoid reporting __builtin__
    else:
        return module + '.' + qualname
