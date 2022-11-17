import os
import typing as t

from icortex.context import ICortexContext

def run_notebook(notebook: str, notebook_args: t.List[str]):
    context = ICortexContext.from_file(notebook)

    vars = context.get_vars()
    import ipdb; ipdb.set_trace()