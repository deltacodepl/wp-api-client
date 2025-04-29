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
import re

sys.path.insert(0, os.path.abspath('..'))

# Get version
with open(os.path.join(os.path.abspath('..'), 'wp_api', '__init__.py'), 'r', encoding='utf-8') as f:
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.M)
    if version_match:
        version = version_match.group(1)
    else:
        version = '0.1.0'

# -- Project information -----------------------------------------------------

project = 'WordPress REST API Python Client'
copyright = '2025, innerkore'
author = 'innerkore'

# The full version, including alpha/beta/rc tags
release = version


# -- General configuration ---------------------------------------------------

# Check for optional extensions
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
]

# Try to load sphinx_autodoc_typehints if available
try:
    import sphinx_autodoc_typehints
    extensions.append('sphinx_autodoc_typehints')
except ImportError:
    print("Note: sphinx_autodoc_typehints extension not found. Type hints will not be processed.")

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Try to load the theme, fallback to alabaster if not available
try:
    import sphinx_rtd_theme
except ImportError:
    html_theme = 'alabaster'
    print("Note: sphinx_rtd_theme not found. Using alabaster theme instead.")

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# -- Extension configuration -------------------------------------------------

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = None

# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'requests': ('https://requests.readthedocs.io/en/master/', None),
}

# -- autodoc configuration ---------------------------------------------------
autodoc_member_order = 'bysource'

# Type hints configuration - only apply if sphinx_autodoc_typehints is available
if 'sphinx_autodoc_typehints' in extensions:
    autodoc_typehints = 'description'