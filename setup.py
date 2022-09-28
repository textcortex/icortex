from setuptools import find_packages, setup


with open("README.md") as f:
    readme = f.read()


setup(
    name="icortex",
    version="0.0.1",
    packages=find_packages(exclude=["tests", "tests.*"]),
    description="Jupyter kernel that allows you generate code from natural language prompts",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="TextCortex Team",
    author_email="onur@textcortex.com",
    url="https://github.com/textcortex/icortex",
    license="Apache",
    python_requires=">=3.7.0",
    install_requires=open("requirements.txt", "r").readlines(),
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
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords=[
        "copilot",
        "tabnine",
        "codex",
        "openai",
        "code generation",
        "code completion",
        "generate code",
        "natural language to python",
        "icortex",
        "textcortex",
        "gpt-3",
        "codegen",
        "polycoder",
        "jupyter notebook",
        "smart jupyter notebook",
        "jupyter notebook kernel",
        "icortex kernel",
    ],
    entry_points={
        "console_scripts": ["icortex=icortex.cli:main"],
    },
)
