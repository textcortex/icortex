<p align="center">
    <a href="https://icortex.ai/"><h2><img src="https://raw.githubusercontent.com/textcortex/icortex/dev-002/assets/logo/banner.svg">ICortex</h2></a>
    <br />
    <a href="https://github.com/textcortex/icortex/workflows/Build/badge.svg"><img src="https://github.com/textcortex/icortex/workflows/Build/badge.svg" alt="Github Actions Status"></a>
    <a href="https://github.com/textcortex/icortex/blob/main/LICENSE"><img src="https://img.shields.io/github/license/textcortex/icortex.svg?color=blue" alt="License"></a>
    <a href="https://www.manim.community/discord/"><img src="https://img.shields.io/discord/997173529235685471.svg?label=discord&color=yellow&logo=discord" alt="Discord"></a>
    <a href="https://discord.textcortex.com/"><img src="https://dcbadge.vercel.app/api/server/QtfGgKneHX?style=flat" alt="Discord"></a>
    <a href="https://pypi.org/project/icortex/"><img src="https://img.shields.io/pypi/v/icortex.svg?style=flat&logo=pypi" alt="PyPI Latest Release"></a>
</p>
<hr />


ICortex is a [Jupyter kernel](https://jupyter-client.readthedocs.io/en/latest/kernels.html) that lets you program using plain English, by generating Python code from natural language prompts:

https://user-images.githubusercontent.com/2453968/196814906-1a0de2a1-27a7-4aec-a960-0eb21fbe2879.mp4

TODO: Prompts are given using the %prompt magic now, update the video accordingly

It is ...

- a drop-in replacement for the IPython kernel. Prompts can be executed with the [magic commands](https://ipython.readthedocs.io/en/stable/interactive/magics.html) `%prompt` or `%p` for short.
- an interface for [Natural Language Programming](https://en.wikipedia.org/wiki/Natural-language_programming) interface—prompts written in plain English automatically generate Python code which can then be executed globally.
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
%icortex init
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

To execute a prompt with ICortex, use the `%prompt` [magic command](https://ipython.readthedocs.io/en/stable/interactive/magics.html) (or `%p` for short) as a prefix. Copy and paste the following prompt into a cell and try to run it:

```
%p print Hello World. Then print the Fibonacci numbers till 100
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
%help
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

You can still access the `icortex` CLI in a Jupyter Notebook or shell by using the magic command `%icortex`. For example running the following in the terminal switches to a local HuggingFace model:

```
icortex service set huggingface
```

To do the same in a Jupyter Notebook, you can run

```
%icortex service set huggingface
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
