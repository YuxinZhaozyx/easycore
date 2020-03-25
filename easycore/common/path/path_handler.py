import logging
import errno
from typing import (
    IO,
    Any,
    Dict,
    List,
    Optional,
    Union,
)
import shutil
import os


class PathHandler(object):
    """
    Base Path handler class for a URI. It routes I/O for a generic
    URI which may look like "protocol://path/to/file".
    """
    def get_cache_dir(self, protocol: Optional[str] = None) -> str:
        """
        Return a cache directory like `<base-cache-dir>/protocol`.

        The <base-cache-dir> is
        
        1) $EASYCORE_CACHE, if set
        2) otherwise ~/.easycore/cache
        
        Args:
            protocol (str or None): protocol such as 'http', 'https'.
                If None, returns the base cache dir.
        """
        cache_dir = os.path.expanduser(os.getenv("EASYCORE_CACHE", "~/.easycore/cache"))
        if protocol is not None:
            cache_dir = os.path.join(cache_dir, protocol)

        return cache_dir

    def get_supported_prefixes(self) -> List[str]:
        """
        Returns:
            List[str]: the list of URI prefixes the PathHandler can support.
        """
        raise NotImplementedError()

    def get_local_path(self, path: str) -> str:
        """
        Get a file path which is compatible with native Python I/O such as
        `open` and `os.path`.

        Args:
            path (str): A URI supported by this PathHandler.
        
        Returns:
            local_path (str): a file path which exists on the local file system.
        """
        raise NotImplementedError()

    def open(self, path: str, mode: str = 'r', **kwargs: Any):
        """
        Open a stream to a URI, similar to the built-in `open`.

        Args:
            path (str): A URI supported by this PathHandler.
            mode (str): Specifies the mode in which the file is opened.
                It defaults to 'r'.
        
        Returns:
            IO: a file-like object.
        """
        raise NotImplementedError()

    def exists(self, path: str) -> bool:
        """
        Checks if there is a resource at the given URI.

        Args:
            path (str): A URI supported by this PathHandler.

        Returns:
            bool: True if the path exists.
        """
        raise NotImplementedError()

    def isfile(self, path: str) -> bool:
        """
        Checks if the resource at the given URI is a file.

        Args:
            path (str): A URI supported by this PathHandler.

        Returns:
            bool: True if the path is a file.
        """
        raise NotImplementedError()

    def isdir(self, path:str) -> bool:
        """
        Checks if the resource at the given URI is a directory.

        Args:
            path (str): A URI supported by this PathHandler.
        
        Returns:
            bool: True if the path is a file.
        """
        raise NotImplementedError()

    def listdir(self, path: str) -> bool:
        """
        List the contents of the directory at the given URI.

        Args:
            path (str): A URI supported by the PathHandler.

        Returns:
            List[str]: list of contents in given path.
        """
        raise NotImplementedError()

    def makedirs(self, path: str) -> None:
        """
        Recursive directory creation function. Similar to `os.makedirs`
        
        Args:
            path (str): A URI supported by this PathHandler.
        """
        raise NotImplementedError()

    def remove(self, path: str) -> None:
        """
        Remove the file (not directory) at the given URI.

        Args:
            path (str): A URI supported by this PathHandler.
        """
        raise NotImplementedError()

    def removedirs(self, path: str) -> None:
        """
        Remove directories recursively.

        Args:
            path (str): A URI supported by this PathHandler.
        """
        raise NotImplementedError()

    def copy_from_local(self, local_path: str, dst_path: str, overwrite: bool = False) -> None:
        """
        Copy a local file to the given URI.

        Args:
            local_path (str): a local file path
            dst_path (str): A URI supported by this PathHandler.
            overwrite (bool): forcing overwirte of existing URI.

        Returns:
            bool: True on success.  
        """
        raise NotImplementedError()

class NativePathHandler(PathHandler):
    """
    PathHandler for local path.
    """
    def get_local_path(self, path: str) -> str:
        """
        Get a file path which is compatible with native Python I/O such as
        `open` and `os.path`.

        Args:
            path (str): A URI supported by this PathHandler.
        
        Returns:
            local_path (str): a file path which exists on the local file system.
        """
        return os.fspath(path)

    def open(self, path: str, mode: str = 'r', **kwargs: Any):
        """
        Open a stream to a URI, similar to the built-in `open`.

        Args:
            path (str): A URI supported by this PathHandler.
            mode (str): Specifies the mode in which the file is opened.
                It defaults to 'r'.
        
        Returns:
            IO: a file-like object.
        """
        return open(path, mode, **kwargs)

    def exists(self, path: str) -> bool:
        """
        Checks if there is a resource at the given URI.

        Args:
            path (str): A URI supported by this PathHandler.

        Returns:
            bool: True if the path exists.
        """
        return os.path.exists(path)

    def isfile(self, path: str) -> bool:
        """
        Checks if the resource at the given URI is a file.

        Args:
            path (str): A URI supported by this PathHandler.

        Returns:
            bool: True if the path is a file.
        """
        return os.path.isfile(path)

    def isdir(self, path:str) -> bool:
        """
        Checks if the resource at the given URI is a directory.

        Args:
            path (str): A URI supported by this PathHandler.
        
        Returns:
            bool: True if the path is a file.
        """
        return os.path.isdir(path)

    def listdir(self, path: str) -> bool:
        """
        List the contents of the directory at the given URI.

        Args:
            path (str): A URI supported by the PathHandler.

        Returns:
            List[str]: list of contents in given path.
        """
        return os.listdir(path)

    def makedirs(self, path: str) -> None:
        """
        Recursive directory creation function. Similar to `os.makedirs`
        
        Args:
            path (str): A URI supported by this PathHandler.
        """
        try:
            os.makedirs(path, exist_ok=True)
        except OSError as e:
            # EEXIST can still happen if multiple processes are creating the dir
            if e.errno != errno.EEXIST:
                raise

    def remove(self, path: str) -> None:
        """
        Remove the file (not directory) at the given URI.

        Args:
            path (str): A URI supported by this PathHandler.
        """
        os.remove(path)

    def removedirs(self, path: str) -> None:
        """
        Remove directories recursively.

        Args:
            path (str): A URI supported by this PathHandler.
        """
        os.removedirs(path)

    def copy_from_local(self, local_path: str, dst_path: str, overwrite: bool = False) -> None:
        """
        Copy a local file to the given URI.

        Args:
            local_path (str): a local file path
            dst_path (str): A URI supported by this PathHandler.
            overwrite (bool): forcing overwirte of existing URI.

        Returns:
            bool: True on success.  
        """
        if self.exists(dst_path) and not overwrite:
            logger = logging.getLogger(__name__)
            logger.error("Destination file {} already exists.".format(dst_path))
            return False

        try:
            dst_path = self.get_local_path(dst_path)
            shutil.copyfile(local_path, dst_path)
            return True
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error("Error in file copy - {}".format(str(e)))
            return False
