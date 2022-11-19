# Guides to writing Jupyter kernels:
# https://jupyter-client.readthedocs.io/en/latest/wrapperkernels.html
# https://github.com/jupyter/jupyter/wiki/Jupyter-kernels

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

from icortex.helper import (
    escape_quotes,
    is_icortex_magic,
)
from icortex.services import get_available_services
from icortex.services.service_base import ServiceBase
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
        # self._run_dialog = types.MethodType(ICortexShell._run_dialog, self)
        self._check_service = types.MethodType(ICortexShell._check_service, self)
        self.print_service_help = types.MethodType(
            ICortexShell.print_service_help, self
        )
        self.run_cell = types.MethodType(ICortexShell.run_cell, self)
        self.cli = types.MethodType(ICortexShell.cli, self)
        self.prompt = types.MethodType(ICortexShell.prompt, self)
        # self.eval_prompt = types.MethodType(ICortexShell.eval_prompt, self)
        self.eval_var = types.MethodType(ICortexShell.eval_var, self)
        self.export = types.MethodType(ICortexShell.export, self)
        self.bake = types.MethodType(ICortexShell.bake, self)

    def set_service(self, service: t.Type[ServiceBase]):
        self.service = service
        return True

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
            service_interaction = self.service.eval_prompt(raw_cell, self.history)
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
        if self._check_service():

            result = self.run_cell(input_, input_type=InputType.PROMPT)
        else:
            print(INIT_SERVICE_MSG)

    def cli(self, input_: str):
        prompt = escape_quotes(input_)
        eval_cli(prompt)

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

    def bake(self, line: str):
        "Bake notebook into a Python script"
        dest = line.split(" ")[0].strip()
        if dest == "":
            raise ValueError("Please specify a destination")

        self.history.bake(dest + ".py")


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
