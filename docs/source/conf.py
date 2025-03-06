# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information


# Get the commit hash from git
import subprocess
import sys
from pathlib import Path

commit_id = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip().decode("utf-8")
print(f"Git Commit ID: {commit_id}")
# patch the Sphinx run so that it can operate directly on the sources
# see: https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#ensuring-the-code-can-be-imported
module_paths = [
    Path("..", "..", "lumigator", "sdk").resolve(),
    Path("..", "..", "lumigator", "schemas").resolve(),
]

for path in module_paths:
    sys.path.append(str(path))


# import the modules that we want to document here to aboid the autodoc error
# see: https://github.com/pydantic/pydantic/discussions/7763#discussioncomment-8417097
from lumigator_sdk import jobs, lm_datasets, models  # noqa: F401, E402

project = "Lumigator 🐊"
copyright = "2024, Mozilla AI"
author = "Mozilla AI Engineering"
release = "0.0.1"

# Add the commit_id to rst_epilog for substitution in reStructuredText files
rst_epilog = f"""
.. {{ commit_id }} replace:: {commit_id}
"""

# Add the commit_id to myst_substitutions for substitution in Markdown files
myst_substitutions = {"commit_id": commit_id}

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.githubpages",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "myst_parser",
    "sphinx_design",
    "sphinx_copybutton",
    "sphinxcontrib.openapi",
]

# napoleon settings
napoleon_include_init_with_doc = True
napoleon_use_admonition_for_examples = True

myst_enable_extensions = [
    "colon_fence",
    "substitution",
]
myst_heading_anchors = 3

templates_path = ["_templates"]
source_suffix = [".rst", ".md"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
copybutton_exclude = ".linenos, .gp, .go"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
# html_static_path = ['_static']
