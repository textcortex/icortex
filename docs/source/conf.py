# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import icortex

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "ICortex"
copyright = "2022, TextCortex Team"
author = "TextCortex Team"
# release = "0.0.3"
release = icortex.__version__
html_title = f"ICortex v{icortex.__version__} docs"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinxcontrib.video",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
]

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]

html_theme_options = {
    "source_repository": "https://github.com/textcortex/ICortex/",
    "source_branch": "main",
    "source_directory": "docs/source/",
    "top_of_page_button": None,
    "light_logo": "logo-bottom-light-bg.svg",
    "dark_logo": "logo-bottom-dark-bg.svg",
    # "light_css_variables": {
    #     "color-content-foreground": "#000000",
    #     "color-background-primary": "#ffffff",
    #     "color-background-border": "#ffffff",
    #     "color-sidebar-background": "#f8f9fb",
    #     "color-brand-content": "#1c00e3",
    #     "color-brand-primary": "#192bd0",
    #     "color-link": "#c93434",
    #     "color-link--hover": "#5b0000",
    #     "color-inline-code-background": "#f6f6f6;",
    #     "color-foreground-secondary": "#000",
    # },
    # "dark_css_variables": {
    #     "color-content-foreground": "#ffffffd9",
    #     "color-background-primary": "#131416",
    #     "color-background-border": "#303335",
    #     "color-sidebar-background": "#1a1c1e",
    #     "color-brand-content": "#2196f3",
    #     "color-brand-primary": "#007fff",
    #     "color-link": "#51ba86",
    #     "color-link--hover": "#9cefc6",
    #     "color-inline-code-background": "#262626",
    #     "color-foreground-secondary": "#ffffffd9",
    # },
}
