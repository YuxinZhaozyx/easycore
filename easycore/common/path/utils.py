import os
import portalocker

def file_lock(path: str):
    """
    A file lock. Once entered, it is guaranteed that no one else holds the same
    lock. Others trying to enter the lock will block for 30 minutes and raise an
    exception.

    This is useful to make sure workers don't cache files to the same location.

    Args:
        path (str): a path to be locked. This function will create a lock named
            `path + ".lock"`.

    Examples:
        
        >>> filename = "/path/to/file"
        >>> with file_lock(filename):
        >>>    if not os.path.isfile(filename):
        >>>        do_create_file()

    """
    dirname = os.path.dirname(path)
    try:
        os.makedirs(dirname, exist_ok=True)
    except OSError:
        pass

    return portalocker.Lock(path + '.lock', timeout=1800)
