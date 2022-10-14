# Guides to writing Jupyter kernels:
# https://jupyter-client.readthedocs.io/en/latest/wrapperkernels.html
# https://github.com/jupyter/jupyter/wiki/Jupyter-kernels

import shlex
import typing as t
from icortex.config import ICortexConfig
from icortex.cli import eval_cli

from ipykernel.ipkernel import IPythonKernel
from traitlets.config.configurable import SingletonConfigurable

from icortex.helper import (
    extract_cli,
    is_cli,
    is_prompt,
    extract_prompt,
    escape_quotes,
    yes_no_input,
    highlight_python,
)
from icortex.services import ServiceBase
from icortex.pypi import install_missing_packages, get_missing_modules
from icortex.defaults import *


class ICortexKernel(IPythonKernel, SingletonConfigurable):
    implementation = "ICortex"
    implementation_version = "0.0.1"
    language = "no-op"
    language_version = "0.1"
    language_info = {
        "name": "any text",
        "mimetype": "text/plain",
        "file_extension": ".py",
        "pygments_lexer": "icortex",
        "codemirror_mode": "text/plain",
    }
    banner = (
        "A prompt-based kernel for interfacing with code-generating language models"
    )

    def __init__(self, **kwargs):

        super().__init__(**kwargs)
        self.service = None
        # self.set_service()

    async def do_execute(
        self,
        input_,
        silent,
        store_history=True,
        user_expressions=None,
        allow_stdin=True,
    ):
        self._forward_input(allow_stdin)

        try:
            if is_cli(input_):
                prompt = extract_cli(input_)
                prompt = escape_quotes(prompt)
                eval_cli(prompt)
                code = ""
            elif is_prompt(input_):
                prompt = extract_prompt(input_)
                prompt = escape_quotes(prompt)

                if self.service is None:
                    conf = ICortexConfig(DEFAULT_ICORTEX_CONFIG_PATH)
                    conf.set_kernel(self)
                    success = conf.set_service()

                    if success:
                        code = self.eval_prompt(prompt)
                    else:
                        print(
                            "No service selected. Run `//service init <service_name>` to initialize a service."
                        )
                        code = ""
                else:
                    code = self.eval_prompt(prompt)
            else:
                code = input_
        finally:
            self._restore_input()

        # TODO: KeyboardInterrupt does not kill coroutines, fix
        # Until then, try not to use Ctrl+C while a cell is executing
        return await IPythonKernel.do_execute(
            self,
            code,
            silent,
            store_history=store_history,
            user_expressions=user_expressions,
            allow_stdin=allow_stdin,
        )

    def set_service(self, service: t.Type[ServiceBase]):
        self.service = service
        return True

    # def set_icortex_service(config_path=DEFAULT_ICORTEX_CONFIG_PATH):
    #     kernel = get_icortex_kernel()
    #     if kernel is not None:
    #         return ICortexConfig(DEFAULT_ICORTEX_CONFIG_PATH).set_service()
    #     return False

    def _run_dialog(
        self,
        code: str,
        execute: bool = False,
        auto_install_packages: bool = DEFAULT_AUTO_INSTALL_PACKAGES,
        quiet: bool = DEFAULT_QUIET,
        nonint: bool = False,
    ):
        scope = self.shell.user_ns

        if not quiet:
            print(highlight_python(code))

        missing_modules = get_missing_modules(code)

        if len(missing_modules) > 0 and not auto_install_packages and not nonint:
            auto_install_packages = yes_no_input(
                f"The following modules are missing in your environment: {', '.join(missing_modules)}\nAttempt to find and install corresponding PyPI packages?"
            )

        unresolved_modules = []
        if auto_install_packages:
            # Unresolved modules are modules that cannot be mapped
            # to any PyPI packages according to the local data in this library
            unresolved_modules = install_missing_packages(code)
            if len(unresolved_modules) > 0:
                print(
                    f"""The following imported modules could not be resolved to PyPI packages: {', '.join(unresolved_modules)}
        Install them manually and try again.
        """
                )
                return ""

        # Modules that are still missing regardless of
        # whether the user tried to auto-install them or not:
        still_missing_modules = get_missing_modules(code)

        if not execute and not nonint and len(still_missing_modules) == 0:
            execute = yes_no_input("Proceed to execute?")

        if execute and len(still_missing_modules) == 0:
            # exec(code, scope)
            return code
        elif execute and len(still_missing_modules) > 0:
            if auto_install_packages:
                bermuda_modules = [
                    module
                    for module in still_missing_modules
                    if module not in unresolved_modules
                ]
                print(
                    f"""These modules should have been installed at this point, but they are still missing:  {', '.join(bermuda_modules)}
    This might be due to an installer issue, please resolve manually.""",
                )
            print(
                f"Skipping execution due to missing modules: {', '.join(still_missing_modules)}."
            )
        return ""

    def eval_prompt(self, prompt_with_args: str):
        service = self.service

        # Print help if the user has typed `/help`
        argv = shlex.split(prompt_with_args)
        args = service.prompt_parser.parse_args(argv)
        prompt = " ".join(args.prompt)
        if prompt == "help":
            return "from icortex import print_help\nprint_help()"

        # Otherwise, generate with the prompt
        response = service.generate(prompt_with_args)
        # TODO: Account for multiple response values
        code_: str = response[0]["text"]

        return self._run_dialog(
            code_,
            execute=args.execute,
            auto_install_packages=args.auto_install_packages,
            quiet=args.quiet,
            nonint=args.nonint,
        )


def get_icortex_kernel() -> ICortexKernel:
    """Get the global ICortexKernel instance.

    Returns None if no ICortexKernel instance is registered.
    """
    if ICortexKernel.initialized():
        return ICortexKernel.instance()


def print_help() -> None:
    icortex_kernel = get_icortex_kernel()
    if icortex_kernel is not None:
        icortex_kernel.service.prompt_parser.print_help()


if __name__ == "__main__":
    from ipykernel.kernelapp import IPKernelApp

    IPKernelApp.launch_instance(kernel_class=ICortexKernel)
