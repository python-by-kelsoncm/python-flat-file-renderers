# docs/conf.py
import os
import sys

# So sphinx-apidoc/autodoc can find flat_file_renderers
sys.path.insert(0, os.path.abspath(".."))

project = "flat_file_renderers"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
    "sphinx.ext.napoleon",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Sphinx 6+ uses root_doc; compatible with master_doc = "index"
root_doc = "index"

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

html_theme_options = {
    "navigation_depth": 4,
    "collapse_navigation": False,
    "sticky_navigation": True,
}
