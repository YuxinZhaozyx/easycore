from setuptools import setup, find_packages

setup(
    name = 'easycore',
    version = '0.1.0',
    author = 'Yuxin Zhao',
    url = 'https://github.com/YuxinZhaozyx/easycore',
    packages = find_packages(),
    install_requires = [
        "pyyaml>=5.3",
    ]
)