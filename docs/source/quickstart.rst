
Quickstart
==========

Installation
------------

Locally
~~~~~~~

Install ICortex on your local machine, along with JupyterLab:

.. code:: sh

   pip install icortex jupyterlab
   python -m icortex.kernel.install

The second line is needed to install the kernel spec into Jupyter, otherwise, you may not be able to see it in JupyterLab. To confirm that the kernel spec is installed, run:

.. code:: sh

   jupyter kernelspec list

ICortex needs to be visible in the list of available kernels.

On Google Colab
~~~~~~~~~~~~~~~

`Google Colab <https://colab.research.google.com/>`__ is a restricted computing environment that does not allow installing new Jupyter kernels. However, you can still use ICortex by running the following code in a Colab notebook:

.. code:: text

   !pip install icortex
   import icortex.init

Using ICortex
-------------

Create a TextCortex account
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tip::
    **This does not require you to enter any payment information.** Your account will receive free credits to try out the service. If you already have an account, you can skip this step.


You need a TextCortex account to connect to TextCortex's code generation API. If you are planning to use a different code generation service, you can skip to :ref:`Start JupyterLab`.

|signup_link|

Once you have an account, proceed to the next section.

Start JupyterLab
~~~~~~~~~~~~~~~~

Create a directory for your new project, and start JupyterLab:

::

   mkdir new-icortex-project
   cd new-icortex-project/
   jupyter lab

Once JupyterLab is up and running, create a new notebook with ICortex kernel. If you are using Google Colab, you can skip this step.

.. important::
    If you don't see ICortex in the list of available kernels, you may have skipped kernel installation above—run ``python -m icortex.kernel.install`` and restart JupyterLab. If you still don't see ICortex there, `create a new installation issue on GitHub <https://github.com/textcortex/icortex/issues/new>`__.

In the new notebook, run in the first cell:

::

   %icortex init

.. tip::
    To run a cell, press Shift+Enter, or click the play symbol ▶ above.

ICortex will then instruct you step by step and create a configuration
file ``icortex.toml`` in your project directory.

.. note::
    If you are not working in JupyterLab, you can run ``icortex init`` directly in the terminal to configure ICortex in your project directory.

After running ``%icortex init`` you should see the following message:

::

    Which code generation service would you like to use?
    Available services: textcortex, huggingface, openai
    Default: textcortex  (Press enter to select the default option)


ICortex supports different code generation services. We recommend that you start with TextCortex. It is selected by default—**press Enter once** to move on to the next step.

In the next step, the dialog will ask whether to use the default parameters for TextCortex's code generation service:

::

   Use default variable values? [Y/n]

**Press Enter once** to choose 'yes' and use the default values. You should see the following message:

.. code:: text

   api_key (If you don't have an API key already, generate one at
   https://app.textcortex.com/user/dashboard/settings/api-key)


Next, |api_key_link|.

Copy your API key from the dashboard, go back to the Jupyter notebook where you initially ran ``%icortex init``, and paste it in the dialog where it was asked for. Press Enter to continue.

You should finally see:

::

   Set service to textcortex successfully.

🎉 Congratulations! ICortex is configured for your current project.

.. note::

    If you use up the starter credits and would like to continue testing out
    ICortex, `hit us up on our Discord on #icortex channel <https://discord.textcortex.com>`__, and we will provide your account with more free credits.


Generate your first code
~~~~~~~~~~~~~~~~~~~~~~~~

ICortex uses the standard IPython `magic
command <https://ipython.readthedocs.io/en/stable/interactive/magics.html>`__ syntax—i.e. commands that are prefixed with ``%`` and ``%%``—for various operations, such as generating code from prompts.

The ``%prompt`` magic command is used to generate Python code. Copy and paste the following prompt into a cell and try to run it:

.. code:: text

   %prompt print Hello World. Then print the Fibonacci numbers till 100

The response may vary, but you should see an output similar to the following:

.. code:: python

   print('Hello World.', end=' ')
   a, b = 0, 1
   while b < 100:
       print(b, end=' ')
       a, b = b, a+b

   Proceed to execute? [Y/n]

ICortex printed the code generated by the API and is now asking whether it should be executed. Press Enter to choose 'yes':

.. code:: text

   Hello World.
   1 1 2 3 5 8 13 21 34 55 89

🎉 Congratulations! You have generated your first Python code using ICortex.

.. important::
    ICortex executes the generated code in the notebook's namespace, so any new variable assigned in the generated code becomes immediately available for access in new notebook cells. Try to print any such variables in a new cell:

    .. code:: python

       print(a, b)

    If your generated code has the same variable names, then this should return:

    .. code:: text

        89, 144

.. tip::
   Try to run the cell that starts with ``%prompt ...`` again. You might notice that the response was faster than the first time you ran it. That is because ICortex caches API responses in a file called ``cache.json`` in your project directory, and uses the cache to serve previous responses for identical requests. This helps you prevent any unnecessary costs in case you would like to run the notebook from scratch.

   To override the default behavior, you can use the ``-r`` or ``--regenerate`` flag at the end of your prompts. This will ensure that the TextCortex API will be called every time the prompt is run.

.. note::
   ICortex adheres to the POSIX argument syntax as implemented by the `Python argparse library <https://docs.python.org/3/library/argparse.html>`__, and provides various command line flags you can use to auto-install missing packages, auto-execute the generated code and so on. Moreover, each new code generation service can easily implement their own flags.
   To see the complete list of options available to your chosen service, run ``%help``:

   .. code:: text

      %help

      usage: %prompt your prompt goes here [-e] [-r] [-i] [-p] ...

      TextCortex Python code generator

      positional arguments:
      prompt                The prompt that describes what the generated Python
                            code should perform.

      options:
      -e, --execute         Execute the Python code returned by the TextCortex API
                            directly.
      -r, --regenerate      Make the kernel ignore cached responses and make a new
                            request to TextCortex API.
      ...



.. Read and analyze a CSV file
.. ~~~~~~~~~~~~~~~~~~~~~~~~~~~


.. |signup_link| raw:: html

   <blockquote><div style="text-align: center"><p><a href="https://app.textcortex.com/user/signup?registration_source=icortex" target="_blank">Click here sign up at TextCortex</a></p></div></blockquote>

.. |api_key_link| raw:: html

   <a href="https://app.textcortex.com/user/dashboard/settings/api-key" target="_blank">click here to visit the dashboard and generate an API key</a>