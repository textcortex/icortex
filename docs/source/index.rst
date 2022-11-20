.. ICortex documentation master file, created by
   sphinx-quickstart on Thu Oct 20 13:49:41 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

:page_template: page.html

ICortex
=======

tl;dr in goes English, out comes Python:

.. video:: https://user-images.githubusercontent.com/2453968/199964302-0dbe1d7d-81c9-4244-a9f2-9d959775e471.mp4
   :width: 100%

ICortex is a no-code development framework that lets you to develop Python programs using plain English. Simply create a recipe that breaks down step-by-step what you want to do in plain English. Our code generating AI will follow your instructions and develop a Python program that suits your needs.

ICortex is designed to be …

-  a drop-in replacement for the `IPython kernel <https://ipython.org/>`__. Prompts can be executed
   via `magic
   commands <https://ipython.readthedocs.io/en/stable/interactive/magics.html>`__
   such as ``%prompt``.
-  interactive—automatically install missing packages, decide whether to
   execute the generated code or not, and so on, directly in the Jupyter
   Notebook cell.
-  open source and fully extensible—ICortex introduces a `domain-specific language <https://en.wikipedia.org/wiki/Domain-specific_language>`__ for orchestrating various code generation services. If you think we are missing a model or an API, you can request it by creating an issue, or implement it yourself by subclassing `ServiceBase` under `icortex/services <https://github.com/textcortex/icortex/tree/main/icortex/services>`__.

Get started
-----------

Visit :doc:`Quickstart<quickstart>` to get started with ICortex.

If you are experiencing any issues or have found a bug, `join our Discord <https://discord.textcortex.com/>`__ to get help.

Index
-----

.. toctree::
   :maxdepth: 2

   quickstart
   reference
   api

.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`
