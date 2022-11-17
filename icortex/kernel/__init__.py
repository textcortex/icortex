# Guides to writing Jupyter kernels:
# https://jupyter-client.readthedocs.io/en/latest/wrapperkernels.html
# https://github.com/jupyter/jupyter/wiki/Jupyter-kernels

import shlex
import sys
import types
import typing as t
from enum import Enum
from logging import warning
from icortex.config import ICortexConfig
from icortex.cli import eval_cli
from icortex.context import ICortexContext

from ipykernel.ipkernel import IPythonKernel
from IPython import InteractiveShell, get_ipython
from IPython.core.interactiveshell import ExecutionResult, ExecutionInfo
from IPython.utils.io import capture_output
from traitlets.config.configurable import SingletonConfigurable

from icortex.helper import (
    escape_quotes,
    serialize_execution_result,
    yes_no_input,
    highlight_python,
)
from icortex.services import get_available_services
from icortex.services.service_base import ServiceBase
from icortex.services.service_interaction import ServiceInteraction
from icortex.pypi import install_missing_packages, get_missing_modules
from icortex.defaults import *
from icortex.var import Var
import importlib_metadata

__version__ = importlib_metadata.version("icortex")

INIT_SERVICE_MSG = (
    r"No service selected. Run `%icortex service init <service_name>` to initialize a service. Candidates: "
    + ", ".join(get_available_services())
)


class InputType(Enum):
    """Enum for input cell type."""

    CODE = 0
    PROMPT = 1
    VAR = 2


def is_icortex_magic(raw_cell: str) -> bool:
    raw_cell = raw_cell.strip()
    return (
        raw_cell.startswith(r"%icortex ")
        or raw_cell.startswith(r"%prompt ")
        or raw_cell.startswith(r"%%prompt ")
        or raw_cell.startswith(r"%p ")
        or raw_cell.startswith(r"%%p ")
        or raw_cell.startswith(r"%var ")
    )


def stream_to_list(stream_str: str) -> t.List[str]:
    ret = []
    for line in stream_str.splitlines():
        # The extra newline is to adhere to nbformat
        ret.append(line + "\n")
    return ret


class ICortexShell(InteractiveShell):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _init_icortex_shell(self):
        self.service = None
        scope = self.user_ns
        self.history = ICortexContext(scope)
        from icortex.magics import load_ipython_extension

        load_ipython_extension(self)
        self.user_ns["get_icortex"] = get_icortex

        # self.var_parser = get_var_magic_parser()

        # Initialize bound methods
        # TODO: make less hacky
        self.set_service = types.MethodType(ICortexShell.set_service, self)
        self._run_dialog = types.MethodType(ICortexShell._run_dialog, self)
        self._check_service = types.MethodType(ICortexShell._check_service, self)
        self.print_service_help = types.MethodType(
            ICortexShell.print_service_help, self
        )
        self.run_cell = types.MethodType(ICortexShell.run_cell, self)
        self.cli = types.MethodType(ICortexShell.cli, self)
        self.prompt = types.MethodType(ICortexShell.prompt, self)
        self.eval_prompt = types.MethodType(ICortexShell.eval_prompt, self)
        self.eval_var = types.MethodType(ICortexShell.eval_var, self)
        self.export = types.MethodType(ICortexShell.export, self)
        self.freeze = types.MethodType(ICortexShell.freeze, self)

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

    # Wrap run_cell
    def run_cell(
        self,
        raw_cell,
        store_history=False,
        silent=False,
        shell_futures=True,
        cell_id=None,
        input_type=InputType.CODE,
    ):

        # Execute generated code
        stdout = ""
        stderr = ""
        # with capture_output() as io:
        #     self.run_cell(
        #         code,
        #         store_history=False,
        #         silent=False,
        #         cell_id=self.execution_count,
        #     )
        #     stdout = io.stdout
        #     stderr = io.stderr
        #     # TODO: Make capture_output() forward streams and display outputs
        #     # This doesn't cause a problem with ipython for some reason but only icortex

        is_icortex_magic_ = is_icortex_magic(raw_cell)
        result = ExecutionResult(ExecutionInfo("", None, None, None, None))

        # print("Called run_cell ", input_type)
        if input_type == InputType.CODE:

            result = InteractiveShell.run_cell(
                self,
                raw_cell,
                store_history=store_history,
                silent=silent,
                shell_futures=shell_futures,
                cell_id=cell_id,
            )
        elif input_type == InputType.PROMPT:
            service_interaction = self.eval_prompt(raw_cell)
            code = service_interaction.get_code()

            result = InteractiveShell.run_cell(
                self,
                code,
                store_history=False,
                silent=False,
                cell_id=self.execution_count,
            )
        elif input_type == InputType.VAR:
            # args = self.var_parser.parse_args(raw_cell.split())
            # code, arg_name, var_name, value = line_to_code(raw_cell)
            var = Var.from_var_magic(raw_cell)
            code = var.get_code()
            result = InteractiveShell.run_cell(
                self,
                code,
                store_history=False,
                silent=False,
                cell_id=self.execution_count,
            )
            self.history.define_var(var)

        # Get the output from InteractiveShell.history_manager.
        # run_cell should be called with store_history=False in order for
        # self.execution_count to match with the respective output
        outputs = []
        try:
            if self.execution_count in self.history_manager.output_hist_reprs:
                output = self.history_manager.output_hist_reprs[self.execution_count]
                # If the cell has an output, add it to the outputs
                # according to nbformat
                outputs.append(
                    {
                        "output_type": "execute_result",
                        "data": {
                            "text/plain": [output],
                        },
                    }
                )
        except:
            warning("There was an issue with saving execution output to history")

        # If cell has an output stream, add it to the outputs
        # TODO: Decide whether to include fields `execution_count`, `metadata`, etc.
        if stdout != "":
            outputs.append(
                {
                    "name": "stdout",
                    "output_type": "stream",
                    "data": {
                        "text/plain": stream_to_list(stdout),
                    },
                }
            )
        # Same for stderr
        if stderr != "":
            outputs.append(
                {
                    "name": "stderr",
                    "output_type": "stream",
                    "data": {
                        "text/plain": stream_to_list(stderr),
                    },
                }
            )

        if input_type == InputType.CODE and not is_icortex_magic_:
            self.history.add_code_cell(
                raw_cell,
                outputs,
                execution_result=result,
            )
        elif input_type == InputType.PROMPT:
            # Store history with the input and corresponding output
            self.history.add_prompt_cell(
                raw_cell,
                outputs,
                service_interaction,
                execution_result=result,
            )
        elif input_type == InputType.VAR:
            self.history.add_var_cell(
                raw_cell,
                var,
                code,
                outputs,
                execution_result=result,
            )

        return result

    def prompt(self, input_: str):
        prompt = escape_quotes(input_)
        if self._check_service():

            result = self.run_cell(prompt, input_type=InputType.PROMPT)
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
            prompt_with_args,
            context=self.history,
            # context=self.history.get_dict(omit_last_cell=True),
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

    def eval_var(self, line: str):
        "Evaluate var magic"
        # args = self.var_parser.parse_args(line.split())
        self.run_cell(line, input_type=InputType.VAR)

    def export(self, line: str):
        "Export notebook to a file"
        dest = line.split(" ")[0].strip()
        if dest == "":
            raise ValueError("Please specify a destination")

        self.history.save_to_file(dest + ".icx")

    def freeze(self, line: str):
        "Freeze notebook into a Python script"
        dest = line.split(" ")[0].strip()
        if dest == "":
            raise ValueError("Please specify a destination")

        self.history.freeze(dest + ".py")


class ICortexKernel(IPythonKernel):
    """Class that implements the ICortex kernel. It is basically
    :class:`ipykernel.ipkernel.IPythonKernel` with magic commands
    and logic for handling code generation.
    """

    implementation = "icortex"
    implementation_version = __version__
    language_info = {
        "name": "python",
        "version": sys.version.split()[0],
        "mimetype": "text/x-python",
        "codemirror_mode": {"name": "ipython", "version": 3},
        "pygments_lexer": "ipython3",
        "nbconvert_exporter": "python",
        "file_extension": ".py",
    }
    banner = "ICortex: Generate Python code from natural language prompts using large language models"
    shell: InteractiveShell

    def __init__(self, **kwargs):

        super().__init__(**kwargs)
        ICortexShell._init_icortex_shell(self.shell)


def get_icortex():
    """Get the global overloaded InteractiveShell instance.

    Returns None if no InteractiveShell instance is registered
    or ICortex has not been initialized yet.
    """
    ret = get_ipython()
    if ret is not None:
        if "prompt" in ret.__dict__:
            return ret
        else:
            return None


def print_service_help() -> None:
    icortex_shell = get_icortex()
    if icortex_shell is not None:
        icortex_shell.print_service_help()


if __name__ == "__main__":
    from ipykernel.kernelapp import IPKernelApp

    IPKernelApp.launch_instance(kernel_class=ICortexKernel)
