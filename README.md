# ICortex Kernel

![Github Actions Status](https://github.com/textcortex/icortex/workflows/Build/badge.svg)
[![License](https://img.shields.io/github/license/textcortex/icortex.svg?color=blue)](https://github.com/textcortex/icortex/blob/main/LICENSE)
[![](https://dcbadge.vercel.app/api/server/QtfGgKneHX?style=flat)](https://discord.textcortex.com/)

ICortex is a [Jupyter kernel](https://jupyter-client.readthedocs.io/en/latest/kernels.html) that lets you program with plain English, by letting you generate Python code from natural language prompts:

https://user-images.githubusercontent.com/2453968/193281898-8f2b4311-2a3a-4bbf-a7d4-b31fcd4f5e08.mp4

It is ...

- a drop-in replacement for the IPython kernel. Prompts start with a forward slash `/`—otherwise the line is treated as regular Python code.
- a [Natural Language Programming](https://en.wikipedia.org/wiki/Natural-language_programming) interface—prompts written in plain English automatically generate Python code which can then be executed in the global namespace.
- interactive—install missing packages directly, decide whether to execute the generated code or not, and so on, directly in the Jupyter Notebook cell.
- open source and fully extensible—if you think we are missing a model or an API, you can request it by creating an issue, or implement it yourself by subclassing `ServiceBase` under [`icortex/services`](icortex/services).

ICortex is currently in alpha, so expect breaking changes. We are giving free credits to our first users—[join our Discord](https://discord.textcortex.com/) to help us shape this product.

## Installation

To install the ICortex Kernel, run the following in the main project directory:

```sh
pip install icortex
```

This will install the Python package and the `icortex` command line interface. You will need to run `icortex` once to install the kernel spec to Jupyter.

## Using ICortex

Before you can use ICortex in Jupyter, you need to configure it for your current project.

If you are using the terminal:

```bash
icortex init
```

Alternatively, you can initialize directly in a Jupyter Notebook ([instructions on how to start JupyterLab](https://jupyterlab.readthedocs.io/en/stable/getting_started/starting.html)):

```
//init
```

The shell will then instruct you step by step and create a configuration file `icortex.toml` in the current directory.

### Choosing a code generation service

ICortex supports different code generation services such as the TextCortex API, OpenAI Codex API, local HuggingFace transformers, and so on.

To use the TextCortex code generation API,

1. [sign up on the website](https://app.textcortex.com/user/signup),
2. [generate an API key on the dashboard](https://app.textcortex.com/user/dashboard/settings/api-key),
3. and proceed to configure `icortex` for your current project:

[![asciicast](https://asciinema.org/a/sTU1EaGFfi3jdSV8Ih7vulsfT.svg)](https://asciinema.org/a/sTU1EaGFfi3jdSV8Ih7vulsfT)

If you use up the starter credits and would like to continue testing out ICortex, [hit us up on our Discord on #icortex channel](https://discord.textcortex.com) and we will charge your account with more free credits.

You can also try out different services e.g. OpenAI's Codex API, if you have access. You can also run code generation models from HuggingFace locally, which we have optimized to run on the CPU—though these produce lower quality outputs due to being smaller.

## Usage

### Executing prompts

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

You can also specify variables or options with command line flags, e.g. to auto-install packages, auto-execute the returned code and so on. To see the complete list of variables for your chosen service, run:

```
/help
```

### Using ICortex CLI

ICortex comes with a full-fledged CLI similar to git or Docker CLI, which you can use to configure how you generate code in your project. To see all the commands you can invoke, run

```sh
icortex help
```

For example the command `icortex service` lets you configure the code generation service you would like to use. To see how to use each command, call them with `help`

```
icortex service help
```

### Accessing ICortex CLI inside Jupyter

You can still access the `icortex` CLI in a Jupyter Notebook or shell by using the prefix `//`. For example running the following in the terminal switches to a local HuggingFace model:

```
icortex service set huggingface
```

To do the same in a Jupyter Notebook, you can run

```
//service set huggingface
```

in a cell, which initializes and switches to the new service directly in your Jupyter session.

## Getting help

Feel free to ask questions in our [Discord](https://discord.textcortex.com/).

## Uninstalling

To uninstall, run

```bash
pip uninstall icortex
```

This removes the package, however, it may still leave the kernel spec in Jupyter's kernel directories, causing it to continue showing up in JupyterLab. If that is the case, run

```
jupyter kernelspec uninstall icortex -y
```
