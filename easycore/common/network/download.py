import logging
import os
import shutil
from typing import Callable, List, Optional
from urllib import request


def download_file(url: str, dir: str, filename: Optional[str] = None, progress: bool = True) -> str:
    """
    Download a file from a given URL to a directory. If the file exists,
    will not overwrite the existing file.

    Args:
        url (str):
        dir (str): the directory to store the file.
        filename (str or None): the basename to save the file. Use the 
            name in the URL if not given.
        progress (bool): whether to use tqdm to draw a progress bar.

    Returns:
        str: the path to the downloaded file or the existing one.
    """
    os.makedirs(dir, exist_ok=True)
    if filename is None:
        filename = os.path.basename(url)

    file_path = os.path.join(dir, filename)

    logger = logging.getLogger(__name__)

    if os.path.isfile(file_path):
        logger.info("File {} exists! Skipping download.".format(filename))
        return file_path
    
    temp = file_path + '.tmp'
    try:
        logger.info("Downloading from {} ...".format(url))
        if progress:
            import tqdm

            def hook(t: tqdm.tqdm) -> Callable[[int, int, Optional[int]], None]:
                last_b: List[int] = [0]

                def inner(b: int, bsize: int, tsize: Optional[int] = None) -> None:
                    if tsize is not None:
                        t.total = tsize
                    t.update((b - last_b[0]) * bsize)
                    last_b[0] = b
                
                return inner

            with tqdm.tqdm(unit = "B", unit_scale=True, miniters=1, desc=filename, leave=True) as t:
                temp, _ = request.urlretrieve(url, filename=temp, reporthook=hook(t))
            
        else:
            temp, _ = request.urlretrieve(url, filename=temp)

        statinfo = os.stat(temp)
        size = statinfo.st_size

        if size == 0:
            raise IOError("Downloaded an empty file from {}!".format(url))

        shutil.move(temp, file_path)
    except IOError:
        logger.error("Failed to download {}".format(url))
        raise
    finally:
        try:
            os.unlink(temp)
        except IOError:
            pass
    
    logger.info("Successfully downloaded {}. {} bytes.".format(file_path, size))
    return file_path


