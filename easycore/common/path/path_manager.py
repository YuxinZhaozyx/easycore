import os
from .path_handler import PathHandler, NativePathHandler
from collections import OrderedDict
from typing import (
    Union,
    MutableMapping,
    Any,
    List,
)

class PathManager(object):
    """
    A general path manager for URI.
    """
    _PATH_HANDLERS: MutableMapping[str, PathHandler] = OrderedDict()
    _NATIVE_PATH_HANDLER = NativePathHandler()


    @staticmethod
    def _get_path_handler(path: Union[str, os.PathLike]) -> PathHandler:
        """
        Finds a PathHandler that supports the given path. Falls back to the native
        PathHandler if no other handler is found.

        Args:
            path (str or os.PathLike): URI path to resource.

        Returns:
            PathHandler: handler
        """
        path = os.fspath(path)
        for prefix in PathManager._PATH_HANDLERS.keys():
            if path.startswith(prefix):
                return PathManager._PATH_HANDLERS[prefix]
        return PathManager._NATIVE_PATH_HANDLER

    @staticmethod
    def register(handler: PathHandler, override: bool = False) -> None:
        """
        Register a path handler.

        Args:
            handler (PathHandler):
            override (bool): allow overriding existing handler for prefix.
        """
        assert isinstance(handler, PathHandler), handler
        for prefix in handler.get_supported_prefixes():
            if not override:
                assert prefix not in PathManager._PATH_HANDLERS
            PathManager._PATH_HANDLERS[prefix] = handler

        # sort path handlers in reverse order so longer prefixes take priority.
        PathManager._PATH_HANDLERS = OrderedDict(
            sorted(
                PathManager._PATH_HANDLERS.items(),
                key = lambda t: t[0],
                reverse = True,
            )
        )

    @staticmethod
    def open(path: str, mode: str = 'r', **kwargs: Any):
        """
        Open a stream to a URI, similar to the built-in `open`.

        Args:
            path (str): A URI supported by registered PathHandler.
            mode (str): Specifies the mode in which the file is opened.
                It defaults to 'r'.
            
            other arguments of built-in `open` such as `encoding` are also available.

        Returns:
            IO: a file-like object.
        """
        return PathManager._get_path_handler(path).open(path, mode, **kwargs)

    @staticmethod
    def copy(src_path: str, dst_path: str, overwrite: bool = False) -> bool:
        """
        Copy a source path to a destination path.

        Args:
            src_path (str): A URI or local path supported by registered PathHandler.
            dst_path (str): A URI or local path supported by registered PathHandler.
            overwrite (bool): forcing overwrite of existing URI.

        Returns:
            bool: True on success.
        """
        src_local_path = PathManager._get_path_handler(src_path).get_local_path(src_path)
        return PathManager._get_path_handler(dst_path).copy_from_local(src_local_path, dst_path, overwrite=overwrite)

    @staticmethod
    def copy_from_local(local_path: str, dst_path: str, overwrite: bool = False) -> bool:
        """
        Copy a resource form local path to destination path.

        Note:
            This interface is for custom PathHandler, it is prefered to use `copy()` instead.

        Args:
            local_path (str): a local path.
            dst_path (str): A URI supported by registered PathHandler.
            overwrite (bool): forcing overwrite of existing URI.
        
        Returns:
            bool: True on success.
        """
        return PathManager.__get_path_handler(dst_path).copy_from_local(local_path, dst_path, overwrite=overwrite)

    @staticmethod
    def get_local_path(path: str) -> str:
        """
        Get a file path which is compatible with native Python I/O such as `open` and `os.path`.

        Note:
            If URI points to a remote resource, this function may download and cache the resource to local disk.

        Args:
            path (str): A URI supported by registered PathHandler.

        Returns:
            str: a file path which exists on the local file system.
        """
        return PathManager._get_path_handler(path).get_local_path(path)

    @staticmethod
    def exists(path: str) -> bool:
        """
        Checks if there is a resource at the given URI.

        Args:
            path (str): A URI supported by registered PathHandler.
        
        Returns:
            bool: True if the path exists.
        """
        return PathManager._get_path_handler(path).exists(path)

    @staticmethod
    def isfile(path: str) -> bool:
        """
        Checks if there the resource at the given URI is a file.

        Args:
            path (str): A URI supported by registered PathHandler.

        Returns:
            bool: True if the path is a file.
        """
        return PathManager._get_path_handler(path).isfile(path)

    @staticmethod
    def isdir(path: str) -> bool:
        """
        Checks if the resource at the given URI is a directory.

        Args:
            path (str): A URI supported by this PathHandler.

        Returns:
            bool: True if the path is a directory.
        """
        return PathManager._get_path_handler(path).isdir(path)

    @staticmethod
    def listdir(path: str) -> List[str]:
        """
        List the contents of the directory at the given URI.

        Args:
            path (str): A URI supported by registered PathHandler.

        Returns:
            List[str]: list of contents in the given path.
        """
        return PathManager._get_path_handler(path).listdir(path)

    @staticmethod
    def makedirs(path: str) -> None:
        """
        Recursive directory creation function. Similar to `os.makedirs()`.

        Args:
            path (str): A URI supported by registered PathHandler.
        """
        PathManager._get_path_handler(path).makedirs(path)

    @staticmethod
    def remove(path: str) -> None:
        """
        Remove the file (not directory) at the given URI.

        Args:
            path (str): A URI supported by registered PathHandler.
        """
        PathManager._get_path_handler(path).remove(path)

    @staticmethod
    def removedirs(path: str) -> None:
        """
        Remove directories recursively.

        Args:
            path (str): A URI supported by registered PathHandler.
        """
        PathManager._get_path_handler(path).removedirs(path)