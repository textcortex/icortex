
Quickstart
==========

Installation
------------

Install ICortex from PyPI, along with JupyterLab:

.. code:: sh

   pip install icortex jupyterlab

   # This line is needed to install the kernel spec to Jupyter:
   python -m icortex.kernel.install

   # Alternatively, running icortex in the terminal also installs the kernel spec:
   icortex

Using ICortex
-------------

Create a directory for your new project, and start JupyterLab:

::

   mkdir new-icortex-project
   cd new-icortex-project/
   jupyter lab

Once JupyterLab is up and running, create a new notebook that uses ICortex. (If you don't see ICortex in the list of available kernels, you may have skipped kernel installation above—run ``python -m icortex.kernel.install`` and restart JupyterLab. If you still don't see ICortex there, `create a new installation issue on GitHub <https://github.com/textcortex/icortex/issues/new>`__.)

In the new notebook, run in the first cell:

::

   %icortex init

ICortex will then instruct you step by step and create a configuration
file ``icortex.toml`` in your project directory.

Alternatively, you can run the following in the terminal to configure ICortex directly without JupyterLab:

.. code:: bash

   icortex init

Choosing a code generation service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

ICortex supports different code generation services such as the
TextCortex API, OpenAI Codex API, local HuggingFace transformers, and so
on.

To use the TextCortex code generation API,

1. `sign up on the website <https://app.textcortex.com/user/signup>`__,
2. `generate an API key on the
   dashboard <https://app.textcortex.com/user/dashboard/settings/api-key>`__,
3. and proceed to configure ``icortex`` for your current project:

If you use up the starter credits and would like to continue testing out
ICortex, `hit us up on our Discord on #icortex
channel <https://discord.textcortex.com>`__ and we will charge your
account with more free credits.

You can also try out different services e.g. OpenAI's Codex API, if you
have access. You can run code generation models from HuggingFace
locally, which we have optimized to run on the CPU—though these produce
lower quality outputs due to being smaller.

Executing prompts
~~~~~~~~~~~~~~~~~

To execute a prompt with ICortex, use the ``%prompt`` `magic
command <https://ipython.readthedocs.io/en/stable/interactive/magics.html>`__
(or ``%p`` for short) as a prefix. Copy and paste the following prompt
into a cell and try to run it:

::

   %p print Hello World. Then print the Fibonacci numbers till 100

Depending on the response, you should see an output similar to the
following:

::

   print('Hello World.', end=' ')
   a, b = 0, 1
   while b < 100:
       print(b, end=' ')
       a, b = b, a+b

   Hello World.
   1 1 2 3 5 8 13 21 34 55 89

You can also specify variables or options with command line flags,
e.g. to auto-install packages, auto-execute the returned code and so on.
To see the complete list of variables for your chosen service, run:

::

   %help

Using ICortex CLI
~~~~~~~~~~~~~~~~~

ICortex comes with a full-fledged CLI similar to git or Docker CLI,
which you can use to configure how you generate code in your project. To
see all the commands you can invoke, run

::

   icortex help

For example the command ``icortex service`` lets you configure the code
generation service you would like to use. To see how to use each
command, call them with ``help``

::

   icortex service help

Accessing ICortex CLI inside Jupyter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can still access the ``icortex`` CLI in a Jupyter Notebook or shell
by using the magic command ``%icortex``. For example running the
following in the terminal switches to a local HuggingFace model:

::

   icortex service set huggingface

To do the same in a Jupyter Notebook, you can run

::

   %icortex service set huggingface

in a cell, which initializes and switches to the new service directly in
your Jupyter session.