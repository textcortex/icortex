.. ICortex documentation master file, created by
   sphinx-quickstart on Thu Oct 20 13:49:41 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

ICortex
=======


ICortex is a `Jupyter kernel <https://jupyter-client.readthedocs.io/en/latest/kernels.html>`__
that lets you program using plain English, by generating Python
code from natural language prompts:

.. video:: https://user-images.githubusercontent.com/2453968/196814906-1a0de2a1-27a7-4aec-a960-0eb21fbe2879.mp4
   :width: 640

It is …

-  a drop-in replacement for the IPython kernel. Prompts start with a
   forward slash ``/``—otherwise the line is treated as regular Python
   code.
-  an interface for `Natural Language
   Programming <https://en.wikipedia.org/wiki/Natural-language_programming>`__—prompts
   written in plain English automatically generate
   Python code which can then be executed globally.
-  interactive—install missing packages directly, decide whether to
   execute the generated code or not, and so on, directly in the Jupyter
   Notebook cell.
-  open source and fully extensible—if you think we are missing a model
   or an API, you can request it by creating an issue, or implement it
   yourself by subclassing ``ServiceBase`` under
   `icortex/services <https://github.com/textcortex/icortex/tree/main/icortex/services>`__.

Get started
-----------

Visit :doc:`Quickstart<quickstart>` to see all the ways you can start using ICortex.

If you are experiencing any problems or bugs, `join our Discord <https://discord.textcortex.com/>`__ to get help.

Index
-----

.. toctree::
   :maxdepth: 2

   quickstart

.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`