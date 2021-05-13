import os
from functools import lru_cache

from box import Box


def _find_metadata_file(path_hint, filename):
    """Search up the directory tree starting at `path_hint` for an existing file with
    the give `filename`.
    """
    if not os.path.exists(path_hint):
        raise IOError('path hint not found')

    if os.path.isfile(path_hint):
        path_hint = os.path.dirname(path_hint)

    last_dir = None
    current_dir = os.path.abspath(path_hint)
    while last_dir != current_dir:
        maybe_path = os.path.join(current_dir, filename)
        if os.path.isfile(maybe_path):
            return maybe_path
        parent_dir = os.path.abspath(os.path.join(current_dir, os.path.pardir))
        last_dir, current_dir = current_dir, parent_dir
    raise IOError('file not found')


@lru_cache()
def _load_frozen_box(path):
    """Load a frozen box from the given file path. File loaded as yaml (which means json will
    usually work).

    Results are cached.
    """
    return Box.from_yaml(filename=path, frozen_box=True)


@lru_cache()
def load_metadata(path_hint, filename='model.yaml'):
    """Attempts to locate and load a model metadata file by searching for a file with
    the given `filename` starting at the directory specified by `path_hint` and walking
    up the filesystem tree. By default the `filename` is assumed to be 'model.yaml'.

    A frozen `dict` instance that supports dotted attribute access is returned.

    If a 'model.yaml' file exists at the project root, the metadata can be loaded as follows:
    ```
        metadata = load_metadata(__file__)
    ```

    Raises `IOError` if the file cannot be found.

    Results are cached.
    """
    file_path = _find_metadata_file(path_hint, filename)
    return _load_frozen_box(file_path)
