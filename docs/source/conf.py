# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import sys
from pathlib import Path

# patch the Sphinx run so that it can operate directly on the sources
# see: https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#ensuring-the-code-can-be-imported
module_paths = [
    Path('..', '..', 'lumigator', 'python', 'mzai', 'sdk').resolve(),
    Path('..', '..', 'lumigator', 'python', 'mzai', 'schemas').resolve()
]

for path in module_paths:
    sys.path.append(str(path))


# import the modules that we want to document here to aboid the autodoc error
# see: https://github.com/pydantic/pydantic/discussions/7763#discussioncomment-8417097
from sdk import jobs, lm_datasets  # noqa: F401, E402

project = 'Lumigator 🐊'
copyright = '2024, Mozilla.ai'
author = 'Dimitris Poulopoulos'
release = '0.0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.githubpages",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "myst_parser",
    "sphinx_design",
    "sphinx_copybutton"
]

# napoleon settings
napoleon_include_init_with_doc = True
napoleon_use_admonition_for_examples = True

myst_enable_extensions = [
    "colon_fence",
]

templates_path = ['_templates']
source_suffix = [".rst", ".md"]
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
copybutton_exclude = ".linenos, .gp, .go"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
# html_static_path = ['_static']
