# Guides to writing Jupyter kernels:
# https://jupyter-client.readthedocs.io/en/latest/wrapperkernels.html
# https://github.com/jupyter/jupyter/wiki/Jupyter-kernels

from logging import warning
import shlex
import typing as t
from icortex.config import ICortexConfig
from icortex.cli import eval_cli
from icortex.context import ICortexHistory

from ipykernel.ipkernel import IPythonKernel
from IPython import InteractiveShell
from traitlets.config.configurable import SingletonConfigurable

from icortex.helper import (
    escape_quotes,
    yes_no_input,
    highlight_python,
)
from icortex.services import ServiceBase, ServiceInteraction, get_available_services
from icortex.pypi import install_missing_packages, get_missing_modules
from icortex.defaults import *
import importlib.metadata

__version__ = importlib.metadata.version("icortex")

INIT_SERVICE_MSG = (
    r"No service selected. Run `%icortex service init <service_name>` to initialize a service. Candidates: "
    + ", ".join(get_available_services())
)


class ICortexKernel(IPythonKernel, SingletonConfigurable):
    implementation = "ICortex"
    implementation_version = __version__
    language = "no-op"
    language_version = "0.1"
    language_info = {
        "name": "icortex",
        "mimetype": "text/x-python",
        "file_extension": ".py",
        "pygments_lexer": "ipython3",
        "codemirror_mode": {"name": "ipython", "version": 3},
    }
    banner = "ICortex: Generate Python code from natural language prompts using large language models"
    shell: InteractiveShell

    def __init__(self, **kwargs):

        super().__init__(**kwargs)
        self.service = None
        scope = self.shell.user_ns
        self.history = ICortexHistory(scope)
        from icortex.magics import load_ipython_extension

        load_ipython_extension(self.shell)

    def set_service(self, service: t.Type[ServiceBase]):
        self.service = service
        return True

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

        install_packages_yesno = False
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

    def _check_service(self):
        if self.service is None:
            conf = ICortexConfig(DEFAULT_ICORTEX_CONFIG_PATH)
            conf.set_kernel(self)
            success = conf.set_service()
            return success
        else:
            return True

    def print_service_help(self):
        if self._check_service():
            self.service.prompt_parser.print_help()
        else:
            print(INIT_SERVICE_MSG)

    def prompt(self, input_: str):
        prompt = escape_quotes(input_)
        if self._check_service():
            service_interaction = self.eval_prompt(prompt)
            code = service_interaction.get_code()
            # Execute generated code
            self.shell.run_cell(
                code,
                store_history=False,
                silent=False,
                cell_id=self.shell.execution_count,
            )
            # Get the output from InteractiveShell.history_manager.
            # run_cell should be called with store_history=False in order for
            # self.shell.execution_count to match with the respective output
            outputs = []
            try:
                if self.shell.execution_count in self.shell.history_manager.output_hist_reprs:
                    output = self.shell.history_manager.output_hist_reprs[self.shell.execution_count]
                    outputs.append(output)
            except:
                warning("There was an issue with saving execution output to history")

            # Store history with the input and corresponding output
            self.history.add_prompt(input_, outputs, service_interaction.to_dict())
        else:
            print(INIT_SERVICE_MSG)

    def cli(self, input_: str):
        prompt = escape_quotes(input_)
        eval_cli(prompt)

    def eval_prompt(self, prompt_with_args: str) -> ServiceInteraction:
        # Print help if the user has typed `/help`
        argv = shlex.split(prompt_with_args)
        args = self.service.prompt_parser.parse_args(argv)

        # Otherwise, generate with the prompt
        response = self.service.generate(
            prompt_with_args, context=self.history.get_dict(omit_last_cell=True)
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


def print_service_help() -> None:
    icortex_kernel = get_icortex_kernel()
    if icortex_kernel is not None:
        icortex_kernel.print_service_help()


if __name__ == "__main__":
    from ipykernel.kernelapp import IPKernelApp

    IPKernelApp.launch_instance(kernel_class=ICortexKernel)
