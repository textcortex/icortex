# ICortex Kernel

![Github Actions Status](https://github.com/textcortex/icortex/workflows/Build/badge.svg)

ICortex is a [Jupyter kernel](https://jupyter-client.readthedocs.io/en/latest/kernels.html) that supercharges your Jupyter Notebook workflow by letting you use code generation services e.g. TextCortex's ICortex API, OpenAI's Codex API, HuggingFace transformers running locally to **generate Python code automatically from user prompts**.

- It is a drop-in replacement for the IPython kernel. Prompts start with a forward slash `/` otherwise the line is treated as regular Python code.
- It is interactive—install missing packages directly, decide whether to execute the generated code or not, directly in the Jupyter Notebook cell.
- It is fully extensible—if you think we are missing a model or an API, you can request it by creating an issue, or implement it yourself by subclassing `ServiceBase` under [`icortex/services`](icortex/services).

## Installation

To install the ICortex Kernel, run the following in the main project directory:

```
pip install icortex
icortex
```

## Launching ICortex

You can launch the ICortex shell directly in your terminal:

```bash
icortex
```

If there is no configuration file `icortex.toml` in the project directory, the shell will prompt you to create one step by step.

Or you can create a new Jupyter notebook. Start the JupyterLab server with

```bash
jupyter lab
```

and choose ICortex as your kernel when creating a new notebook.

## Usage

To execute a prompt with ICortex, use the `/` character (forward slash, also used to denote division) as a prefix. Copy and paste the following prompt into a cell and try to run it:

```
/print Hello World. Then print the Fibonacci numbers till 100, all in the same line
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

You can make the kernel attempt to auto-install packages and auto-execute the returned code.

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