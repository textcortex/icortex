
Reference
=========

ICortex is a `Jupyter kernel <https://jupyter-client.readthedocs.io/en/latest/kernels.html>`__ that provides a `soft-programming <https://en.wikipedia.org/wiki/Soft_computing>`__ environment, allowing anyone to create programs with informal and imprecise language. Prompts written in natural language are used to generate Python code at runtime.

ICortex overloads the regular `IPython kernel <https://ipython.org/>`__ with `magic commands <https://ipython.readthedocs.io/en/stable/interactive/magics.html>`__ that provide code-generation capabilities and fine-grained control over generation context. As such, ICortex can run an existing IPython notebook without any compatibility issues. Cells that contain regular Python are executed in the global scope as usual.

The history of code generation and execution is saved in hidden variables and is used to construct the context for each new code generation. In other words, API calls to generate code in a cell contains information about previously ran prompts, executed cells, their outputs and other metadata related to the notebook.

Magic commands
--------------

``%prompt`` or ``%p``
~~~~~~~~~~~~~~~~~~~~~

The ``%prompt`` magic is used

.. code:: ipython

   %prompt This is a prompt and will be used to generate code


.. code:: python



.. currentmodule:: icortex

.. automodule:: icortex
   :members:
   :undoc-members: