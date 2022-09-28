import os
from setuptools import find_packages, setup
from setuptools.command.install import install


with open("README.md") as f:
    readme = f.read()


class PostInstallCommand(install):
    def run(self) -> None:
        install.run(self)
        # from icortex.install import main as install_kernel

        # install_kernel([])


setup(
    name="icortex",
    version="0.0.1",
    packages=find_packages(exclude=["tests", "tests.*"]),
    description="Jupyter kernel that allows you generate code from natural language prompts",
    long_description=readme,
    author="TextCortex Team",
    author_email="onur@textcortex.com",
    url="https://github.com/textcortex/icortex",
    python_requires=">=3.7.0",
    install_requires=[
        "click",
        "ipykernel",
        "ipython",
        "ipywidgets",
        "jupyter-client",
        "jupyter-console",
        "jupyter-core",
        "jupyterlab-widgets",
        "openai",
        "pygments",
        "toml",
        "traitlets",
    ],
    extras_require={
        "huggingface": [
            "torch",
            "transformers",
            "optimum",
            "onnx",
            "onnxruntime",
        ],
        "openai": [
            "openai",
        ],
    },
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
    ],
    cmdclass={"install": PostInstallCommand},
    entry_points={
        "console_scripts": ["icortex=icortex.cli:main"],
    },
)
