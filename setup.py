from setuptools import setup, find_packages

setup(
    name = 'easycore',
    version = '0.3.3',
    author = 'Yuxin Zhao',
    url = 'https://github.com/YuxinZhaozyx/easycore',
    packages = find_packages(),
    license = 'LICENSE',
    description = 'a collection of tools to support research and development.',
    long_description = open('README.md', encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    install_requires = [
        "pyyaml",
    ]
)
