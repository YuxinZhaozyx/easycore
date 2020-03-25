from easycore.common.path import PathManager, RedirectPathHandler
import os

CURRENT_DIR = os.path.dirname(__file__)

def test_native_copy():
    source_path = os.path.join(CURRENT_DIR, "./test.md")
    copy_path = os.path.join(CURRENT_DIR, "./test_copy.md")
    
    assert not PathManager.exists(copy_path)
    PathManager.copy(source_path, copy_path)
    assert PathManager.exists(copy_path)
    PathManager.remove(copy_path)
    assert not PathManager.exists(copy_path)

def test_native_open():
    with PathManager.open(os.path.join(CURRENT_DIR, "./test.md"), 'r', encoding='utf-8') as f:
        assert len(f.read()) > 0

def test_http_open():
    with PathManager.open("https://github.com/YuxinZhaozyx/easycore/raw/master/README.md", 'r', encoding='utf-8') as f:
        assert len(f.read()) > 0

def test_redirect_makedirs():
    dir = os.path.join(CURRENT_DIR, "testdir")
    PathManager.register(RedirectPathHandler("easycore://", dir))
    PathManager.makedirs("easycore://path-for-test")
    assert PathManager.isdir("easycore://path-for-test")
    PathManager.removedirs("easycore://path-for-test")
    assert not PathManager.exists("easycore://path-for-test")

