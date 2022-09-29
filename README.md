# ICortex Kernel

![Github Actions Status](https://github.com/textcortex/icortex/workflows/Build/badge.svg)
[![License](https://img.shields.io/github/license/textcortex/icortex.svg?color=blue)](https://github.com/textcortex/icortex/blob/main/LICENSE)
[![](https://dcbadge.vercel.app/api/server/QtfGgKneHX?style=flat)](https://discord.textcortex.com/)

ICortex is a [Jupyter kernel](https://jupyter-client.readthedocs.io/en/latest/kernels.html) that supercharges your Jupyter Notebook workflow by letting you generate **generate Python code automatically from natural language prompts**.

It is ...

- a drop-in replacement for the IPython kernel. Prompts start with a forward slash `/`—otherwise the line is treated as regular Python code.
- interactive—install missing packages directly, decide whether to execute the generated code or not, directly in the Jupyter Notebook cell.
- open source and fully extensible—if you think we are missing a model or an API, you can request it by creating an issue, or implement it yourself by subclassing `ServiceBase` under [`icortex/services`](icortex/services).

ICortex is currently in alpha, so expect breaking changes. We are giving free credits to our first users—[join our Discord](https://discord.textcortex.com/) to help us shape this product.

## Installation

To install the ICortex Kernel, run the following in the main project directory:

```sh
pip install icortex
```

This install the Python package and the `icortex` command line interface. You will need to run `icortex` once to install the kernel spec to Jupyter.

## Using ICortex

Before you can use ICortex in Jupyter, you need to configure it for your current project.

To do that, simply launch the ICortex shell in your terminal:

```bash
icortex
```

The shell will instruct you step by step and create a configuration file `icortex.toml` in your current directory.

### Choosing a code generation service

ICortex supports different code generation services such as the TextCortex code generation API, OpenAI Codex API, local HuggingFace transformers, and so on.

To use the TextCortex code generation API,

1. [sign up on the website](https://app.textcortex.com/user/signup),
2. [generate an API key on the dashboard](https://app.textcortex.com/user/dashboard/settings/api-key),
3. and proceed to configure `icortex` for your current project:

[![asciicast](https://asciinema.org/a/sTU1EaGFfi3jdSV8Ih7vulsfT.svg)](https://asciinema.org/a/sTU1EaGFfi3jdSV8Ih7vulsfT)

If you use up the starter credits and would like to continue testing out ICortex, [hit us up on our Discord on #icortex channel](https://discord.textcortex.com) and we will charge your account with more free credits.

You can also try out different services e.g. OpenAI's Codex API, if you have access. You can also run code generation models from HuggingFace locally, which we have optimized to run on the CPU—though these produce lower quality outputs due to being smaller.

### Launch JupyterLab

Now that ICortex is configured for your project, you can launch JupyterLab:

```bash
jupyter lab
```

and choose ICortex as your kernel when creating a new notebook.

## Usage

To execute a prompt with ICortex, use the `/` character (forward slash, also used to denote division) as a prefix. Copy and paste the following prompt into a cell and try to run it:

```
/print Hello World. Then print the Fibonacci numbers till 100
```

Depending on the response, you should see an output similar to the following:

```
print('Hello World.', end=' ')
a, b = 0, 1
while b < 100:
    print(b, end=' ')
    a, b = b, a+b

Hello World.
1 1 2 3 5 8 13 21 34 55 89
```

You can also specify options with command line flags, e.g. to auto-install packages, auto-execute the returned code and so on. To see the complete list of options for your chosen service, run:

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
