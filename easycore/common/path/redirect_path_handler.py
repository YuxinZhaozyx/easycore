from .path_manager import PathManager
from .path_handler import PathHandler
from typing import (
    IO,
    List,
    Dict,
    Any,
)

class RedirectPathHandler(PathHandler):
    """
    Redirect a new prefix to existed prefix.

    Example:
        .. code-block:: python
            
            PathManager.register(RedirectPathHandler("easycore://", "http://xxx.com/download/"))
    """
    def __init__(self, new_prefix: str, old_prefix: str):
        self.new_prefix = new_prefix
        self.old_prefix = old_prefix

    def get_supported_prefixes(self) -> List[str]:
        """
        Returns:
            List[str]: the list of URI prefixes the PathHandler can support.
        """
        return [self.new_prefix]

    def redirect(self, path: str) -> str:
        """
        Redirect path from new_prefix to old_prefix path.

        Args:
            path (str): path of new_prefix.

        Returns:
            str: path of old_prefix.
        """
        return path.replace(self.new_prefix, self.old_prefix, 1)

    def get_local_path(self, path: str) -> str:
        """
        Get a file path which is compatible with native Python I/O such as
        `open` and `os.path`.

        Args:
            path (str): A URI supported by this PathHandler.
        
        Returns:
            local_path (str): a file path which exists on the local file system.
        """
        return PathManager.get_local_path(self.redirect(path))

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
        return PathManager.open(self.redirect(path), mode, **kwargs)

    def exists(self, path: str) -> bool:
        """
        Checks if there is a resource at the given URI.

        Args:
            path (str): A URI supported by this PathHandler.

        Returns:
            bool: True if the path exists.
        """
        return PathManager.exists(self.redirect(path))

    def isfile(self, path: str) -> bool:
        """
        Checks if the resource at the given URI is a file.

        Args:
            path (str): A URI supported by this PathHandler.

        Returns:
            bool: True if the path is a file.
        """
        return PathManager.isfile(self.redirect(path))

    def isdir(self, path:str) -> bool:
        """
        Checks if the resource at the given URI is a directory.

        Args:
            path (str): A URI supported by this PathHandler.
        
        Returns:
            bool: True if the path is a file.
        """
        return PathManager.isdir(self.redirect(path))
        

    def listdir(self, path: str) -> bool:
        """
        List the contents of the directory at the given URI.

        Args:
            path (str): A URI supported by the PathHandler.

        Returns:
            List[str]: list of contents in given path.
        """
        return PathManager.listdir(self.redirect(path))

    def makedirs(self, path: str) -> None:
        """
        Recursive directory creation function. Similar to `os.makedirs`
        
        Args:
            path (str): A URI supported by this PathHandler.
        """
        PathManager.makedirs(self.redirect(path))

    def remove(self, path: str) -> None:
        """
        Remove the file (not directory) at the given URI.

        Args:
            path (str): A URI supported by this PathHandler.
        """
        PathManager.remove(self.redirect(path))

    def removedirs(self, path: str) -> None:
        """
        Remove directories recursively.

        Args:
            path (str): A URI supported by this PathHandler.
        """
        PathManager.removedirs(self.redirect(path))

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
        return PathManager.copy_from_local(local_path, self.redirect(dst_path), overwrite=overwrite)
        