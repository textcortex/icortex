import json
import typing as t
from icortex.var import Var
import importlib_metadata
from copy import deepcopy
import platform
from icortex.defaults import DEFAULT_CONTEXT_VAR

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


class ICortexContext:
    """Interface to construct a history variable in globals for storing
    notebook context.
    The constructed dict maps to JSON, and the schema is compatible
    with the
    `Jupyter notebook format <https://nbformat.readthedocs.io/en/latest/format_description.html>`__:
    """

    def __init__(self, scope: t.Dict[str, t.Any]):
        self.scope = scope
        self._check_init()

    def _check_init(self):
        if DEFAULT_CONTEXT_VAR not in self.scope:
            self.scope[DEFAULT_CONTEXT_VAR] = deepcopy(INITIAL_HISTORY_VAL)

        self._dict = self.scope[DEFAULT_CONTEXT_VAR]

    def get_dict(self, omit_last_cell=False):
        ret = deepcopy(self._dict)
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

    def add_code_cell(
        self,
        code: str,
        outputs: t.List[t.Any],
        execution_result: t.Optional[t.Dict[str, t.Any]] = None,
    ):
        self._check_init()

        ret = {
            "cell_type": "code",
            "metadata": {"source_type": "code"},
            "source": code,
            "outputs": outputs,
        }
        if execution_result:
            ret["metadata"]["execution_result"] = execution_result

        self._dict["cells"].append(ret)
        return ret

    def add_var_cell(
        self,
        var_line: str,
        code: str,
        outputs: t.List[t.Any],
        execution_result: t.Optional[t.Dict[str, t.Any]] = None,
    ):
        self._check_init()

        ret = {
            "cell_type": "code",
            "metadata": {"source_type": "var", "code": code},
            "source": var_line,
            "outputs": outputs,
        }
        if execution_result:
            ret["metadata"]["execution_result"] = execution_result

        self._dict["cells"].append(ret)
        return ret

    def add_prompt_cell(
        self,
        prompt: str,
        outputs: t.List[t.Any],
        service_interaction: t.Dict[str, t.Any],
        execution_result: t.Optional[t.Dict[str, t.Any]] = None,
    ):
        self._check_init()

        ret = {
            "cell_type": "code",
            # It is actually a prompt, but "code" here refers to the Jupyter cell type
            "metadata": {
                # Any ICortex specific information needs to be stored here to
                # adhere to the Jupyter notebook format
                "source_type": "prompt",  # This tells that the input was a prompt
                "service": service_interaction,
            },
            "source": prompt,
            "outputs": outputs,
        }
        if execution_result:
            ret["metadata"]["execution_result"] = execution_result

        self._dict["cells"].append(ret)
        return ret

    def save_to_file(self, path: str):
        self._check_init()
        with open(path, "w") as f:
            json.dump(self.get_dict(), f, indent=2)

        print("Exported to", path)