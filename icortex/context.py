import json
import os
import typing as t
from icortex.var import Var
import importlib_metadata
from abc import ABC, abstractclassmethod
from copy import deepcopy
import platform
from icortex.defaults import DEFAULT_CONTEXT_VAR
from icortex.services import ServiceInteraction
from IPython.core.interactiveshell import ExecutionResult, ExecutionInfo

from icortex.helper import serialize_execution_result

icortex_version = importlib_metadata.version("icortex")

INITIAL_HISTORY_VAL = {
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
    @abstractclassmethod
    def __init__(self):
        raise NotImplementedError

    @abstractclassmethod
    def get_code(self):
        raise NotImplementedError

    @abstractclassmethod
    def to_dict(self):
        raise NotImplementedError


class CodeCell(Cell):
    def __init__(
        self,
        code: str,
        outputs: t.List[t.Any],
        execution_result: ExecutionResult = None,
    ):
        self.code = code
        self.outputs = outputs
        self.execution_result = execution_result

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
        self.execution_result = execution_result

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


class VarCell(ABC):
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
        self.execution_result = execution_result

    def to_dict(self):
        ret = {
            "cell_type": "code",
            "metadata": {"source_type": "var", "code": self.code},
            "source": self.var_line,
            "outputs": self.outputs,
        }
        if self.execution_result:
            ret["metadata"]["execution_result"] = serialize_execution_result(
                self.execution_result
            )

        return ret


class ICortexContext:
    """Interface to construct a history variable in globals for storing
    notebook context.
    The constructed dict maps to JSON, and the schema is compatible
    with the
    `Jupyter notebook format <https://nbformat.readthedocs.io/en/latest/format_description.html>`__:
    """

    def __init__(self, scope: t.Dict[str, t.Any] = None):
        self.scope = scope
        self.cells = []
        self._check_init()

    def _check_init(self):
        if self.scope is None:
            return

        if DEFAULT_CONTEXT_VAR not in self.scope:
            self.scope[DEFAULT_CONTEXT_VAR] = deepcopy(INITIAL_HISTORY_VAL)

        self._dict = self.scope[DEFAULT_CONTEXT_VAR]

    def to_dict(self, omit_last_cell=False):
        ret = deepcopy(self._dict)
        # Serialize cells and add to the return value
        cells = [cell.to_dict() for cell in self.cells]
        ret.update({"cells": cells})

        if omit_last_cell:
            if len(ret["cells"]) > 0:
                del ret["cells"][-1]
        return ret

    def define_var(self, var: Var):
        self._check_init()
        if "variables" not in self._dict["metadata"]:
            self._dict["metadata"]["variables"] = []

        self._dict["metadata"]["variables"].append(var.to_dict())
        return

    def add_code_cell(self, *args, **kwargs):
        self._check_init()
        cell = CodeCell(*args, **kwargs)
        self.cells.append(cell)
        return cell

    def add_var_cell(self, *args, **kwargs):
        self._check_init()
        cell = VarCell(*args, **kwargs)
        self.cells.append(cell)
        return cell

    def add_prompt_cell(self, *args, **kwargs):
        self._check_init()
        cell = PromptCell(*args, **kwargs)
        self.cells.append(cell)
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
        ret._dict = dict_
        return ret

    def get_vars(self):
        """Returns a list of all variables defined in the notebook"""
        self._check_init()
        if "variables" not in self._dict["metadata"]:
            return []
        return [Var.from_dict(v) for v in self._dict["metadata"]["variables"]]
