<p align="center">
    <a href="https://icortex.ai/"><img src="https://raw.githubusercontent.com/textcortex/icortex/main/assets/logo/banner.svg"></a>
    <br />
    <br />
    <a href="https://github.com/textcortex/icortex/workflows/Build/badge.svg"><img src="https://github.com/textcortex/icortex/workflows/Build/badge.svg" alt="Github Actions Status"></a>
    <a href="https://pypi.org/project/icortex/"><img src="https://img.shields.io/pypi/v/icortex.svg?style=flat&logo=pypi" alt="PyPI Latest Release"></a>
    <a href="https://pepy.tech/project/icortex"><img src="https://pepy.tech/badge/icortex/month?" alt="Downloads"> </a>
    <a href="https://icortex.readthedocs.io/en/latest/?badge=latest"><img src="https://readthedocs.org/projects/icortex/badge/?version=latest" alt="Documentation Status"></a>
    <a href="https://github.com/textcortex/icortex/blob/main/LICENSE"><img src="https://img.shields.io/github/license/textcortex/icortex.svg?color=blue" alt="License"></a>
    <a href="https://discord.textcortex.com/"><img src="https://dcbadge.vercel.app/api/server/QtfGgKneHX?style=flat" alt="Discord"></a>
    <a href="https://twitter.com/TextCortex/"><img src="https://img.shields.io/twitter/url/https/twitter.com/cloudposse.svg?style=social&label=Follow%20%40TextCortex" alt="Twitter"></a>
    <br />
    <br />
    <i>A Python library for <a href="https://en.wikipedia.org/wiki/Soft_computing">soft-code</a> development — program in plain English with AI code generation!</i>
</p>
<hr />

ICortex is a [Jupyter kernel](https://jupyter-client.readthedocs.io/en/latest/kernels.html) that lets you develop **soft programs**:

- sets of instructions (i.e. prompts) [written in natural language](https://en.wikipedia.org/wiki/Natural-language_programming) (such as English)
- processed by language models that generate Python code
- to perform useful work in various contexts
- more flexibly than regular software.

To put it simply—in goes English, out comes Python:

https://user-images.githubusercontent.com/2453968/196814906-1a0de2a1-27a7-4aec-a960-0eb21fbe2879.mp4

TODO: Prompts are given using the %prompt magic now, update the video accordingly

ICortex is ...

- a drop-in replacement for the IPython kernel. Prompts can be executed with the [magic commands](https://ipython.readthedocs.io/en/stable/interactive/magics.html) `%prompt` or `%p` for short.
- interactive—install missing packages directly, decide whether to execute the generated code or not, and so on, directly in the Jupyter Notebook cell.
- open source and fully extensible—if you think we are missing a model or an API, you can request it by creating an issue, or implement it yourself by subclassing `ServiceBase` under [`icortex/services`](icortex/services).

It is similar to [Github Copilot](https://github.com/features/copilot) but with certain differences that make it stand out:

| Feature | GitHub Copilot | ICortex |
|---|:---:|:---:|
| Generates code ... | In the text editor | In a [Jupyter kernel](https://docs.jupyter.org/en/latest/projects/kernels.html) (language backend that provides the execution environment) |
| From ... | Existing code and comments | Plain English prompts |
| Level of control over context used to generate code | Low | High |
| Plain language instructions are ... | Just comments | Standalone programs |
| The resulting program is ... | Static | Dynamic—adapts to the context it is executed in |
| Can connect to different code generation APIs | No | Yes |

The main difference between ICortex and a code-generation plugin like GitHub Copilot is that ICortex is a programming paradigm similar to [literate programming](https://en.wikipedia.org/wiki/Literate_programming) or [natural language programming](https://en.wikipedia.org/wiki/Natural-language_programming), where the natural language prompt is the first-class citizen, and which allows for fine-grained control over the code-generation context.

ICortex is currently in alpha, so expect breaking changes. We are giving free credits to our first users—[join our Discord](https://discord.textcortex.com/) to help us shape it.

## Installation

Install directly from PyPI:

```sh
pip install icortex
# This line is needed to install the kernel spec to Jupyter:
python -m icortex.kernel.install
```

## Quickstart

[Click here to visit the docs and get started using ICortex](https://icortex.readthedocs.io/en/latest/quickstart.html).

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
