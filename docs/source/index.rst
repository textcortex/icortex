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

ICortex enables you to develop **soft programs**:

   *Soft program:* a set of instructions (i.e. prompts) `written in natural language <https://en.wikipedia.org/wiki/Natural-language_programming>`__ (e.g. English), processed by a language model that generates code at a lower layer of abstraction (e.g. Python), to perform work more flexibly than regular software.

In other words, ICortex is a **natural language programming** (NLP) framework that enables you to write code in English, and then run it in Python. It aims to make programming more accessible to non-programmers.

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
