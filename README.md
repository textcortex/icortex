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
    <i>A no-code development framework — Let AI do the coding for you 🦾</i>
</p>
<hr />

tl;dr in goes English, out comes Python:

https://user-images.githubusercontent.com/2453968/199964302-0dbe1d7d-81c9-4244-a9f2-9d959775e471.mp4

ICortex is a no-code development framework that lets you to develop Python programs using plain English. Simply create a recipe that breaks down step-by-step what you want to do in plain English. Our code generating AI will follow your instructions and develop a Python program that suits your needs.

[Create a TextCortex account](https://app.textcortex.com/user/signup?registration_source=icortex) to receive free starter credits and start using ICortex.

## Try it out

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/textcortex/icortex-binder/HEAD?filepath=basic_example.ipynb)

You can try out ICortex directly in your browser. Launch a Binder instance by clicking [here](https://mybinder.org/v2/gh/textcortex/icortex-binder/HEAD?filepath=basic_example.ipynb), and follow the [instructions in our docs](https://docs.icortex.ai/en/latest/quickstart.html#using-icortex) to get started.

Alternatively, you can use ICortex in Google Colab if you have an account. See [below](#on-google-colab).

[Check out the documentation](https://docs.icortex.ai/) to learn more. [Join our Discord](https://discord.textcortex.com/) to get help.

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

Note that the package needs to be installed to every new Google Colab runtime—you may need to reinstall if it ever gets disconnected.

## Quickstart

[Click here to get started using ICortex](https://icortex.readthedocs.io/en/latest/quickstart.html).

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
