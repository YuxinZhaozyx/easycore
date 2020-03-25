# Path manage tools

**easycore** make it easy to manage local path and remote path in the same way.

## Manage local path

```python
from easycore.common.path import PathManager

# open a local path
with PathManager.open("/path/to/file", 'r', encoding='utf-8') as f:
    print(f.read())

# check file or directory exists, similar to `os.path.exists`
PathManager.exists('/path/to/file')

# isfile and isdir, similar to `os.path.isfile` and `os.path.isdir`.
success = PathManager.isfile('/path/to/file')
success = PathManager.isdir('/path/to/dir')

# makedirs, similar to `os.makedirs(path, exist_ok=True)`.
PathManager.makedirs('/path/to/dir')

# remove file (no directory), similar to `os.remove`. 
PathManager.remove('/path/to/file')

# remove directoreis, similar to `os.path.removedirs`.
PathManager.removedirs('/path/to/dir')

# list directory, similar to 'os.listdir`.
list_content = PathManager.listdir('/path/to/dir')

# copy
PathManager.copy("/path/to/file2", "/destination/path")

```

## Manage remote URL

You can manage remote path (http/https/ftp URL) which may look like `http://xxx.com/yyy.txt`.

The remote file will be first downloaded and cached. The cache directory is set by

1. environment variable `$EASYCORE_CACHE`, if set.
2. otherwise, `~/.easycore/cache`.

```python
from easycore.common.path import PathManager

# open a remote path
with PathManager.open("http://xxx.com/yyy.txt", 'r', encoding='utf-8') as f:
    print(f.read())

# get local path
local_path = PathManager.get_local_path("http://xxx.com/yyy.txt")
```

You can copy the file to a local path.

```python
# copy remote file to local path.
PathManager.copy("http://xxx.com/yyy.txt", "/a/local/path")
```

## Redirect path

You can redirect a path to anywhere in local or remote.

For example, if you have uploaded a file to a remote server and you can access it throuth URL `http://xxx.com/download/yyy/zzz.txt`, `PathManager` make it possible to redirect `easycore://` prefix to `http://xxx.com/download` so that you can access the resource with path `easycore://yyy/zzz.txt`.

```python
from easycore.common.path import PathManager, RedirectPathHandler

PathManager.register(RedirectPathHandler("easycore://", "http://xxx.com/download/"))
```

You can also redirect to a local path.

```python
from easycore.common.path import PathManager, RedirectPathHandler

PathManager.register(RedirectPathHandler("file://", "/path/to/dir/"))
```

This feature is very useful in redirecting dataset path. For example, my dataset directories are at `e:\\Dataset\\MNIST`, `e:\\Dataset\\CIFAR100` and `f:\\ImageNet`.

```python
from easycore.common.path import PathManager, RedirectPathHandler

PathManager.register(RedirectPathHandler("dataset://MNIST/", "e:\\Dataset\\MNIST\\"))
PathManager.register(RedirectPathHandler("dataset://CIFAR100/", "e:\\Dataset\\CIFAR100\\"))
PathManager.register(RedirectPathHandler("dataset://ImageNet/", "f:\\ImageNet\\"))
```

Now, I can access them with path `dataset://<dataset-name>/`.


## Custom PathHandler

The behaviors of `PathManager` is defined by the registered `PathHandler`s.

You can also custom a new `PathHandler` and register it to `PathManager`. 

For example, if you want to redirect the http and https cache directory without setting `$EASYCORE_CACHE`, you can custom the `HTTPURLHandler` by yourself.

```python
from easycore.common.path import PathManager, HTTPURLHandler
import os

# custom PathHandler
class NewHTTPURLHandler(HTTPURLHandler):
    def get_cache_dir(self, protocol):
        cache_dir = os.path.expanduser(os.getenv("NEW_CACHE", "~/.easycore/cache"))
        if protocol is not None:
            cache_dir = os.path.join(cache_dir, protocol)
        return cache_dir

    def get_support_prefixes(self):
        return ["http://", "https://"]

# register custom path handler
PathManager.register(NewHTTPURLHandler(), override=True) # set override to True to override the existing http and https path handler.
```

Now, you can set cache directory through `$NEW_CACHE`.

See the detail implement of [`NativePathHandler`](../_modules/easycore/common/path/path_handler.html#NativePathHandler), [`HTTPURLHandler`](../_modules/easycore/common/path/http_path_handler.html#HTTPURLHandler), [`RedirectPathHandler`](../_modules/easycore/common/path/redirect_path_handler.html#RedirectPathHandler) for more custom path handler examples.


## API Documentation

+ [easycore.common.path](../modules/easycore.common.path.html)