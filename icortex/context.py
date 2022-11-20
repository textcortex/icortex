import json
import logging
import os
import typing as t
import argparse
from icortex.var import Var
import importlib_metadata
from abc import ABC, abstractclassmethod
from copy import deepcopy
import platform
from icortex.defaults import DEFAULT_CONTEXT_VAR
from icortex.services.service_interaction import ServiceInteraction
from IPython.core.interactiveshell import ExecutionResult, ExecutionInfo

from icortex.helper import (
    comment_out,
    unescape_quotes,
    serialize_execution_result,
    deserialize_execution_result,
    is_magic,
)

icortex_version = importlib_metadata.version("icortex")

EMPTY_CONTEXT = {
    "metadata": {
        "kernelspec": {
            "display_name": "ICortex (Python 3)",
            "language": "python",
            "name": "icortex",
        },
        "language_info": {
            "pygments_lexer": "ipython3",
            "codemirror_mode": {"name": "ipython", "version": 3},
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "icortex",
            "nbconvert_exporter": "python",
            "pygments_lexer": "ipython3",
            "version": icortex_version,
            "python_version": platform.python_version(),
        },
    },
    "nbformat": 4,
    "nbformat_minor": 5,
    "cells": [],
}


class Cell(ABC):
    def __init__(self, execution_result: ExecutionResult = None):
        self.execution_result = execution_result

    @abstractclassmethod
    def get_code(self) -> str:
        raise NotImplementedError

    @abstractclassmethod
    def to_dict(self) -> t.Dict[str, t.Any]:
        raise NotImplementedError

    @property
    def success(self) -> bool:
        if self.execution_result is None:
            return False
        return self.execution_result.success


class CodeCell(Cell):
    def __init__(
        self,
        code: str,
        outputs: t.List[t.Any],
        execution_result: ExecutionResult = None,
    ):
        self.code = code
        self.outputs = outputs
        super().__init__(execution_result=execution_result)

    def get_code(self):
        return self.code

    def to_dict(self):
        ret = {
            "cell_type": "code",
            "metadata": {"source_type": "code"},
            "source": self.code,
            "outputs": self.outputs,
        }
        if self.execution_result:
            ret["metadata"]["execution_result"] = serialize_execution_result(
                self.execution_result
            )

        return ret

    def from_dict(d: t.Dict[str, t.Any]):
        return CodeCell(
            d["source"],
            d["outputs"],
            execution_result=deserialize_execution_result(
                d["metadata"]["execution_result"]
            ),
        )

    def get_code(self) -> str:
        return self.code


class PromptCell(Cell):
    def __init__(
        self,
        prompt: str,
        outputs: t.List[t.Any],
        service_interaction: ServiceInteraction,
        execution_result: ExecutionResult = None,
    ):
        self.prompt = prompt
        self.outputs = outputs
        self.service_interaction = service_interaction
        super().__init__(execution_result=execution_result)

    def to_dict(self):
        ret = {
            "cell_type": "code",
            # It is actually a prompt, but "code" here refers to the Jupyter cell type
            "metadata": {
                # Any ICortex specific information needs to be stored here to
                # adhere to the Jupyter notebook format
                "source_type": "prompt",  # This tells that the input was a prompt
                "service": self.service_interaction.to_dict(),
            },
            "source": self.prompt,
            "outputs": self.outputs,
        }
        if self.execution_result:
            ret["metadata"]["execution_result"] = serialize_execution_result(
                self.execution_result
            )
        return ret

    def from_dict(d: t.Dict[str, t.Any]):
        return PromptCell(
            d["source"],
            d["outputs"],
            ServiceInteraction.from_dict(d["metadata"]["service"]),
            deserialize_execution_result(d["metadata"]["execution_result"]),
        )

    def get_code(self) -> str:
        return self.service_interaction.get_code()

    def get_commented_code(self):
        # Add the prompt as a comment
        ret = comment_out(self.prompt.rstrip()) + "\n\n"
        # Add the generated code
        ret += self.get_code().rstrip().replace("\n\n", "\n")
        return ret


class VarCell(Cell):
    def __init__(
        self,
        var_line: str,
        var: Var,
        code: str,
        outputs: t.List[t.Any],
        execution_result: ExecutionResult = None,
    ):
        self.var_line = var_line
        self.var = var
        self.code = code
        self.outputs = outputs
        super().__init__(execution_result=execution_result)

    def to_dict(self):
        ret = {
            "cell_type": "code",
            "metadata": {
                "source_type": "var",
                "var": self.var.to_dict(),
                "code": self.code,
            },
            "source": self.var_line,
            "outputs": self.outputs,
        }
        if self.execution_result:
            ret["metadata"]["execution_result"] = serialize_execution_result(
                self.execution_result
            )

        return ret

    def from_dict(d: t.Dict[str, t.Any]):
        return VarCell(
            d["source"],
            Var.from_dict(d["metadata"]["var"]),
            d["metadata"]["code"],
            d["outputs"],
            deserialize_execution_result(d["metadata"]["execution_result"]),
        )

    def get_code(self):
        return self.code


class ICortexContext:
    """Interface to construct a history variable in globals for storing
    notebook context.
    The constructed dict maps to JSON, and the schema is compatible
    with the
    `Jupyter notebook format <https://nbformat.readthedocs.io/en/latest/format_description.html>`__:
    """

    def __init__(self, scope: t.Dict[str, t.Any] = None):
        self.scope = scope
        self._cells = []
        self._vars = []
        self._check_init()

    def _check_init(self):
        if self.scope is None:
            return

        if self.scope.get(DEFAULT_CONTEXT_VAR) != self:
            self.scope[DEFAULT_CONTEXT_VAR] = self

        # if DEFAULT_CONTEXT_VAR not in self.scope:

        # self._dict = self.scope[DEFAULT_CONTEXT_VAR]

    def to_dict(self, omit_last_cell=False):
        ret = deepcopy(EMPTY_CONTEXT)
        # ret = deepcopy(self._dict)
        # Serialize cells and add to the return value
        cells = [cell.to_dict() for cell in self._cells]
        ret.update({"cells": cells})
        # Serialize vars and add to the return value
        vars = [var.to_dict() for var in self._vars]
        ret["metadata"].update({"variables": vars})

        if omit_last_cell:
            if len(ret["cells"]) > 0:
                del ret["cells"][-1]
        return ret

    def define_var(self, var: Var):
        self._vars.append(var)
        # self._check_init()
        # if "variables" not in self._dict["metadata"]:
        #     self._dict["metadata"]["variables"] = []

        # self._dict["metadata"]["variables"].append(var.to_dict())
        return

    def add_code_cell(self, *args, **kwargs):
        self._check_init()
        cell = CodeCell(*args, **kwargs)
        self._cells.append(cell)
        return cell

    def add_var_cell(self, *args, **kwargs):
        self._check_init()
        cell = VarCell(*args, **kwargs)
        self._cells.append(cell)
        return cell

    def add_prompt_cell(self, *args, **kwargs):
        self._check_init()
        cell = PromptCell(*args, **kwargs)
        self._cells.append(cell)
        return cell

    def save_to_file(self, path: str):
        self._check_init()
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

        print("Exported to", path)

    def from_file(path: str, scope: t.Dict[str, t.Any] = None):
        # Check if the file exists
        if not os.path.exists(path):
            raise FileNotFoundError(f"File {path} does not exist")

        with open(path, "r") as f:
            dict_ = json.load(f)

        ret = ICortexContext(scope=scope)

        for cell_dict in dict_["cells"]:
            if cell_dict["metadata"]["source_type"] == "code":
                cell = CodeCell.from_dict(cell_dict)
            elif cell_dict["metadata"]["source_type"] == "var":
                cell = VarCell.from_dict(cell_dict)
            elif cell_dict["metadata"]["source_type"] == "prompt":
                cell = PromptCell.from_dict(cell_dict)
            else:
                raise ValueError(
                    f"Unknown cell type {cell_dict['metadata']['source_type']}"
                )
            ret._cells.append(cell)

        ret._vars = [Var.from_dict(v) for v in dict_["metadata"]["variables"]]

        return ret

    @property
    def vars(self):
        """Returns a list of all variables defined in the notebook"""
        return self._vars

    def iter_cells(self) -> t.Iterator[Cell]:
        for cell in self._cells:
            yield cell

    def run(self, notebook_args: t.List[str]):
        """Run the notebook with the given arguments"""

        vars = self.vars
        parsed_args = get_notebook_arg_parser(vars).parse_args(notebook_args)
        scope = locals()

        for cell in self.iter_cells():
            if cell.success:
                if isinstance(cell, VarCell):
                    var = cell.var
                    # Change the value to that of the parsed argument
                    var.value = var._type(getattr(parsed_args, var.arg))
                    code = var.get_code()
                else:
                    code = cell.get_code()
                # Execute the returned code
                exec(code, scope)

    def bake(self, dest_path: str, format=True):
        """Bake the notebook to a Python script"""

        # Warn if the extension is not .py
        if not dest_path.endswith(".py"):
            print(
                f"Warning: {dest_path} does not have the .py extension. "
                "It is recommended that you use the .py extension for "
                "frozen files."
            )

        vars = self.vars
        scope = locals()

        output = "import argparse\n\nparser = argparse.ArgumentParser()\n"
        for var in vars:
            output += f"parser.add_argument({var.arg!r}, type={var._type.__name__})\n"
        output += "args = parser.parse_args()\n\n"

        for cell in self.iter_cells():
            if cell.success:
                if isinstance(cell, VarCell):
                    var = cell.var
                    # Change the value to that of the parsed argument
                    # var.value = var._type(getattr(parsed_args, var.arg))
                    code = f"{var.name} = args.{var.arg}\n\n"
                    # code = var.get_code()
                elif isinstance(cell, CodeCell):
                    if not is_magic(cell.get_code()):
                        code = cell.get_code().rstrip() + "\n\n"
                    else:
                        continue
                elif isinstance(cell, PromptCell):
                    code = cell.get_commented_code().rstrip() + "\n\n"

                # Execute the returned code
                output += code

        # Run black over output
        if format:
            import black
            try:
                output = black.format_str(output, mode=black.FileMode())
            except:
                logging.warning("Failed to format code with black")

        with open(dest_path, "w") as f:
            f.write(output)

        print("Baked to", dest_path)


def get_notebook_arg_parser(vars: t.List[Var]):
    parser = argparse.ArgumentParser(add_help=False)
    for var in vars:
        parser.add_argument(
            var.arg,
            type=var._type,
            help=var.description,
        )
    return parser
