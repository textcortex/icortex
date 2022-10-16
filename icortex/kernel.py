# Guides to writing Jupyter kernels:
# https://jupyter-client.readthedocs.io/en/latest/wrapperkernels.html
# https://github.com/jupyter/jupyter/wiki/Jupyter-kernels

import shlex
import typing as t
from icortex.config import ICortexConfig
from icortex.cli import eval_cli
from icortex.context import ICortexHistory

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
from icortex.services import ServiceBase, ServiceInteraction
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
        scope = self.shell.user_ns
        self.history = ICortexHistory(scope)

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
                        service_interaction = self.eval_prompt(prompt)
                        code = service_interaction.get_code()

                        # TODO: Store output once #12 is implemented
                        self.history.add_prompt(
                            input_, [], service_interaction.to_dict()
                        )
                    else:
                        print(
                            "No service selected. Run `//service init <service_name>` to initialize a service."
                        )
                        code = ""
                else:
                    service_interaction = self.eval_prompt(prompt)
                    code = service_interaction.get_code()
                    # TODO: Store output once #12 is implemented
                    self.history.add_prompt(input_, [], service_interaction.to_dict())

            else:
                code = input_
                # TODO: Store output once #12 is implemented
                self.history.add_code(code, [])

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
        auto_execute: bool = DEFAULT_AUTO_EXECUTE,
        auto_install_packages: bool = DEFAULT_AUTO_INSTALL_PACKAGES,
        quiet: bool = DEFAULT_QUIET,
        nonint: bool = False,
    ) -> ServiceInteraction:

        if not quiet:
            print(highlight_python(code))

        missing_modules = get_missing_modules(code)

        if len(missing_modules) > 0 and not auto_install_packages and not nonint:
            install_packages_yesno = yes_no_input(
                f"The following modules are missing in your environment: {', '.join(missing_modules)}\nAttempt to find and install corresponding PyPI packages?"
            )
        install_packages = auto_install_packages or install_packages_yesno

        unresolved_modules = []
        if install_packages:
            # Unresolved modules are modules that cannot be mapped
            # to any PyPI packages according to the local data in this library
            unresolved_modules = install_missing_packages(code)
            if len(unresolved_modules) > 0:
                print(
                    f"""The following imported modules could not be resolved to PyPI packages: {', '.join(unresolved_modules)}
        Install them manually and try again.
        """
                )

        # Modules that are still missing regardless of
        # whether the user tried to auto-install them or not:
        still_missing_modules = get_missing_modules(code)

        execute_yesno = False
        if not auto_execute and not nonint and len(still_missing_modules) == 0:
            execute_yesno = yes_no_input("Proceed to execute?")

        execute = auto_execute or execute_yesno

        if execute and len(still_missing_modules) > 0:
            execute = False
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

        return ServiceInteraction(
            name=self.service.name,
            execute=execute,
            outputs=[code],
            quiet=quiet,
            install_packages=install_packages,
            missing_modules=missing_modules,
            # unresolved_modules=unresolved_modules,
            # still_missing_modules=still_missing_modules,
        )

    def eval_prompt(self, prompt_with_args: str) -> ServiceInteraction:
        # Print help if the user has typed `/help`
        argv = shlex.split(prompt_with_args)
        args = self.service.prompt_parser.parse_args(argv)
        prompt = " ".join(args.prompt)
        if prompt == "help":
            return "from icortex import print_help\nprint_help()"

        # Otherwise, generate with the prompt
        response = self.service.generate(
            prompt_with_args, context=self.history.get_dict()
        )
        # TODO: Account for multiple response values
        code_: str = response[0]["text"]

        return self._run_dialog(
            code_,
            auto_execute=args.execute,
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
