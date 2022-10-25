import typing as t
import importlib.metadata
from copy import deepcopy
import platform
from icortex.defaults import DEFAULT_HISTORY_VAR

icortex_version = importlib.metadata.version("icortex")

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


class ICortexHistory:
    """Interface to construct a history variable in globals for storing
    notebook context.
    The constructed dict maps to JSON, and the schema is compatible
    with the Jupyter notebook format:
    https://nbformat.readthedocs.io/en/latest/format_description.html"""

    def __init__(self, scope: t.Dict[str, t.Any]):
        self.scope = scope
        self._check_init()

    def _check_init(self):
        if DEFAULT_HISTORY_VAR not in self.scope:
            self.scope[DEFAULT_HISTORY_VAR] = deepcopy(INITIAL_HISTORY_VAL)

        self._dict = self.scope[DEFAULT_HISTORY_VAR]

    def get_dict(self, omit_last_cell=False):
        ret = deepcopy(self._dict)
        if omit_last_cell:
            if len(ret["cells"]) > 0:
                del ret["cells"][-1]
        return ret

    def add_code(self, code: str, outputs: t.List[t.Any]):
        self._check_init()

        ret = {
            "cell_type": "code",
            "metadata": {},
            "source": code,
            "outputs": outputs,
        }

        self._dict["cells"].append(ret)
        return ret

    def add_prompt(
        self,
        prompt: str,
        outputs: t.List[t.Any],
        service_interaction: t.Dict[str, t.Any],
    ):
        self._check_init()

        ret = {
            "cell_type": "code",
            "metadata": {
                "service": service_interaction,
            },
            "source": prompt,
            "outputs": outputs,
        }

        self._dict["cells"].append(ret)
        return ret
