
Reference
=========

ICortex is a `Jupyter kernel <https://jupyter-client.readthedocs.io/en/latest/kernels.html>`__ that provides a `soft-programming <https://en.wikipedia.org/wiki/Soft_computing>`__ environment, allowing anyone to create programs with less formal and precise language. Prompts written in natural language are used to generate Python code at runtime.

ICortex overloads the regular `IPython kernel <https://ipython.org/>`__ with `magic commands <https://ipython.readthedocs.io/en/stable/interactive/magics.html>`__ that provide code-generation capabilities and fine-grained control over generation context. As such, ICortex can run an existing IPython notebook without any compatibility issues. Cells that contain regular Python are executed in the current namespace as usual.

Code generation and execution history is saved in hidden variables and is used to construct the context for each new code generation. In other words, API calls to generate code in a cell contain information about previously ran prompts, executed cells, their outputs and other metadata related to the notebook.

Magic commands
--------------

``%prompt``
~~~~~~~~~~~

The ``%prompt`` magic is used to describe what the generated code should perform.
Running the command passes the prompt to
:func:`ServiceBase.generate() <icortex.services.service_base.ServiceBase.generate>`.
Each service defines how to parse the prompt and generate code
individually—each class that derives from ServiceBase
provides :attr:`prompt_parser <icortex.services.service_base.ServiceBase.prompt_parser>`
to parse the prompt and retrieve parameter values.


.. code:: ipython

   %prompt This is a prompt and will be used to generate code

The string that follows the prompt is parsed by
`argparse.ArgumentParser <https://docs.python.org/3/library/argparse.html>`__:

.. code:: ipython

   %prompt You can change how a prompt is run by providing flags -r --max-tokens 128

You can escape flags by surrounding the prompt text in single or double quotes:

.. code:: ipython

   %prompt "This flag -r is parsed verbatim"

Running ``%help`` prints a list of all the options you can generate code with your
chosen service:

.. tip::
    ICortex provides the alias magic ``%p``, to let you write
    prompts faster:

    .. code :: ipython

       %p This is the same as calling "%prompt ..."

.. ``%icortex``
.. ~~~~~~~~~~~~