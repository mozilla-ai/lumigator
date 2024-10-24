# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
sys.path.insert(0, os.path.abspath('../../lumigator/python/mzai/backend'))  # Source code dir relative to this file
sys.path.insert(0, os.path.abspath('../../lumigator/python/mzai/sdk'))  # Source code dir relative to this file
sys.path.insert(0, os.path.abspath('../../lumigator/python/mzai/schemas'))  # Source code dir relative to this file
# sys.path.insert(0, os.path.abspath('../../lumigator/python/mzai'))  # Source code dir relative to this file

project = "lumigator"
author = "Vicki Boykis, Davide Eynard, Kyle White"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "nbsphinx",
    "myst_parser",
    "sphinx_codeautolink",
    'sphinx.ext.napoleon',
    'sphinx.ext.autodoc', # Generate doc from docstrings
    'sphinx.ext.autosummary',  # Create neat summary tables
]

# use language set by highlight directive if no language is set by role
inline_highlight_respect_highlight = False

# use language set by highlight directive if no role is set
inline_highlight_literals = False

autosummary_generate = True  # Turn on sphinx.ext.autosummary

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

source_suffix = [".rst", ".md"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = []
