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

tl;dr in goes English, out comes Python:

https://user-images.githubusercontent.com/2453968/199964302-0dbe1d7d-81c9-4244-a9f2-9d959775e471.mp4

ICortex enables you to develop **soft programs**:

> *Soft program:* a set of instructions (i.e. prompts) [written in natural language](https://en.wikipedia.org/wiki/Natural-language_programming) (e.g. English), processed by a language model that generates code at a lower layer of abstraction (e.g. Python), to perform work more flexibly than regular software.

In other words, ICortex is a **natural language programming** (NLP) framework that enables you to write code in English, and then run it in Python. It aims to make programming more accessible to non-programmers.

ICortex is designed to be …

- a drop-in replacement for the [IPython kernel](https://ipython.org/). Prompts are executed via [magic commands](https://ipython.readthedocs.io/en/stable/interactive/magics.html) such as `%prompt`.
- interactive—automatically install missing packages, decide whether to execute the generated code or not, and so on, directly in the Jupyter Notebook cell.
- open source and fully extensible—ICortex introduces a [domain-specific language](https://en.wikipedia.org/wiki/Domain-specific_language) for orchestrating various code generation services. If you think we are missing a model or an API, you can request it by creating an issue, or implement it yourself by subclassing `ServiceBase` under [`icortex/services`](icortex/services).

ICortex is similar to [Github Copilot](https://github.com/features/copilot) but with certain differences that make it stand out:

| Feature | GitHub Copilot | ICortex |
|---|:---:|:---:|
| Generates code ... | In the text editor | At runtime through a [Jupyter kernel](https://docs.jupyter.org/en/latest/projects/kernels.html) |
| Control over code generation context ... | No | Yes |
| Natural language instructions are a ... | Second-class citizen (Code comes first) | First-class citizen (Prompts *are* the program) |
| The resulting program is ... | Static | Dynamic—adapts to the context |
| Can connect to different code generation APIs | No | Yes |

The main difference between ICortex and a code-generation plugin like GitHub Copilot is that ICortex is a new paradigm for [Natural Language Programming](https://en.wikipedia.org/wiki/Natural-language_programming) where the *prompt* is the first-class citizen. GitHub Copilot, on the other hand, enhances the existing paradigm that are already used by developers.

ICortex is currently in alpha, so expect breaking changes. We are giving free credits to our first users—[join our Discord](https://discord.textcortex.com/) to request more if you finish the starter credits.

## Installation

### Locally

Install directly from PyPI:

```sh
pip install icortex
# This line is needed to install the kernel spec to Jupyter:
python -m icortex.kernel.install
```

### On Google Colab

[Google Colab](https://colab.research.google.com/) is a restricted computing environment that does not allow installing new Jupyter kernels. However, you can still use ICortex by running the following code in a Colab notebook:

```
!pip install icortex
import icortex.init
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
