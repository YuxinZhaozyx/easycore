# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import sphinx_rtd_theme

import mock
DEPLOY = os.environ.get("READTHEDOCS") == "True"

# -- Project information -----------------------------------------------------

project = 'easycore'
copyright = '2020, Yuxin Zhao'
author = 'Yuxin Zhao'

try:
    import torch
except ImportError:
    for m in [
        "torch",
        "torchvision",
        "torch.nn",
        "torch.nn.parallel",
        "torch.distributed",
        "torch.multiprocessing",
        "torch.autograd",
        "torch.autograd.function",
        "torch.nn.modules",
        "torch.nn.modules.utils",
        "torch.utils",
        "torch.utils.data",
        "torchvision",
        "torchvision.ops",
    ]:
        sys.modules[m] = mock.Mock(name=m)

for m in [
    "yaml",
    "cv2",
]:
    sys.modules[m] = mock.Mock(name=m)

sys.modules["cv2"].__version__ = "3.4"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'sphinx.ext.napoleon',
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
    'sphinx_rtd_theme',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# -- Configurations for plugins ------------
napoleon_google_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_special_with_doc = True
napoleon_numpy_docstring = False
napoleon_use_rtype = False
autodoc_inherit_docstrings = False
autodoc_member_order = "bysource"

if DEPLOY:
    intersphinx_timeout = 10
else:
    # skip this when building locally
    intersphinx_timeout = 0.1

intersphinx_mapping = {
    "python": ("https://docs.python.org/3.6", None),
    "numpy": ("https://docs.scipy.org/doc/numpy/", None),
    "torch": ("https://pytorch.org/docs/master/", None),
}

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']


source_parsers = {
   '.md': 'recommonmark.parser.CommonMarkParser',
}

source_suffix = ['.rst', '.md']

master_doc = 'index'
