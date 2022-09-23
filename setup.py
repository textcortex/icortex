import os
from setuptools import setup
from setuptools.command.install import install


with open("README.md") as f:
    readme = f.read()


class PostInstallCommand(install):
    def run(self) -> None:
        install.run(self)
        os.system("python -m icortex.install")
        # from icortex.install import main
        # main()


setup(
    name="icortex",
    version="0.0.1",
    packages=["icortex"],
    description="Jupyter kernel for using code generation API's",
    long_description=readme,
    author="TextCortex Team",
    author_email="ceyhun@textcortex.com",
    url="https://github.com/textcortex/icortex",
    install_requires=["jupyter_client", "IPython", "ipykernel"],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
    ],
    cmdclass={"install": PostInstallCommand},
)
