# ICortex

ICortex is a [Jupyter kernel](https://jupyter-client.readthedocs.io/en/latest/kernels.html) which uses the TextCortex API and can automatically generate Python code from user prompts. This functionality can be used in tandem with the regular Jupyter Notebook workflow to increase work efficiency.

## Installation

To install the ICortex Kernel, run the following in the main project directory:

```
pip install .
python -m icortex.install
```

This will change once the package is deployed to PyPI.

## Launching ICortex

You can launch ICortex directly in Jupyter console:

```bash
jupyter console --kernel icortex
```

Or you can create a new Jupyter notebook. Start the JupyterLab server with

```bash
jupyter lab
```

and choose ICortex as your kernel when creating a new notebook.

## Usage

To execute a prompt with ICortex, use the `/` character (forward slash, also used to denote division) as a prefix. Copy and paste the following prompt into a cell and try to run it:

```
/ print Hello World. Then print the Fibonacci numbers till 100, all in the same line -e
```

If all goes well, you should see an output similar to the following:

```
print('Hello World.', end=' ')
a, b = 0, 1
while b < 100:
    print(b, end=' ')
    a, b = b, a+b

Hello World.
1 1 2 3 5 8 13 21 34 55 89
```

ICortex first printed the code generated code, executed it, and returned the output below the cell. This is because we gave it the `-e` option, which stands for `--execute`. You can omit this flag next time when you just want to display the generated code without executing.

To see all the options you can use with ICortex, simply run:

```
/help
```

## Uninstalling

To uninstall, run

```bash
pip uninstall icortex
```

This removes the package, however, it may still leave the kernel spec in Jupyter's kernel directories, causing it to continue showing up in JupyterLab. If that is the case, run

```
jupyter kernelspec uninstall icortex -y
```


<!-- This is useful to run this together with the install command when debugging the library:

```bash
sudo jupyter kernelspec uninstall icortex -y; sudo jupyter kernelspec install ICortex; jupyter console --kernel icortex  -->
