from easycore.common.network import download_file
import os

def test_download_file():
    url = "https://github.com/YuxinZhaozyx/easycore/archive/v0.3.4.zip"
    dir = os.path.dirname(__file__)
    file_path = download_file(url, dir)

    os.remove(file_path)
    

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)

    test_download_file()