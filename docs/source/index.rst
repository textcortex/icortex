.. ICortex documentation master file, created by
   sphinx-quickstart on Thu Oct 20 13:49:41 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

ICortex
=======


ICortex is a `Jupyter
kernel <https://jupyter-client.readthedocs.io/en/latest/kernels.html>`__
that lets you develop **soft programs**:

-  sets of instructions (i.e. prompts) `written in natural
   language <https://en.wikipedia.org/wiki/Natural-language_programming>`__
   (such as English)
-  processed by language models that generate Python code
-  to perform useful work in various contexts
-  more flexibly than regular software.

To put it simply—in goes English, out comes Python:

.. video:: https://user-images.githubusercontent.com/2453968/196814906-1a0de2a1-27a7-4aec-a960-0eb21fbe2879.mp4
   :width: 640

ICortex is …

-  a drop-in replacement for the IPython kernel. Prompts can be executed
   with the `magic
   commands <https://ipython.readthedocs.io/en/stable/interactive/magics.html>`__
   ``%prompt`` or ``%p`` for short.
-  interactive—install missing packages directly, decide whether to
   execute the generated code or not, and so on, directly in the Jupyter
   Notebook cell.
-  open source and fully extensible—if you think we are missing a model
   or an API, you can request it by creating an issue, or implement it
   yourself by subclassing ``ServiceBase`` under
   `icortex/services <https://github.com/textcortex/icortex/tree/main/icortex/services>`__.

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
