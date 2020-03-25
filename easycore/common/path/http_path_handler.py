import logging
from urllib.parse import urlparse, unquote
from hashlib import md5
from typing import (
    IO,
    List,
    Dict,
    Any,
)
import os
from easycore.common.network import download_file

from .utils import file_lock
from .path_handler import PathHandler

class HTTPURLHandler(PathHandler):
    """
    Download URLs and cache them to disk.
    """
    def __init__(self) -> None:
        self.cache_map: Dict[str, str] = {}

    def get_supported_prefixes(self) -> List[str]:
        """
        Returns:
            List[str]: the list of URI prefixes the PathHandler can support.
        """
        return ["http://", "https://", "ftp://"]

    def get_local_path(self, path: str) -> str:
        """
        Get a file path which is compatible with native Python I/O such as
        `open` and `os.path`.

        Args:
            path (str): A URI supported by this PathHandler.
        
        Returns:
            local_path (str): a file path which exists on the local file system.
        """
        if path not in self.cache_map or not os.path.exists(self.cache_map[path]):
            logger = logging.getLogger(__name__)
            parsed_url = urlparse(path)
            host_dir = md5(parsed_url.netloc.encode()).hexdigest()
            file_path = unquote(parsed_url.path.lstrip('/'))
            file_path = os.path.join(self.get_cache_dir(parsed_url.scheme), host_dir, file_path)

            dirname, filename = os.path.split(file_path)
            with file_lock(file_path):
                if not os.path.isfile(file_path):
                    logger.info("Downloading {} ...".format(path))
                    file_path = download_file(path, dirname, filename=filename)
            logger.info("URL {} cached in {}.".format(path, file_path))
            self.cache_map[path] = file_path
        return self.cache_map[path]            

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
        local_path = self.get_local_path(path)
        return open(local_path, mode, **kwargs)
