import os
import typing as t
import argparse

from icortex.context import ICortexContext, VarCell
from icortex.var import Var


def get_notebook_arg_parser(vars: t.List[Var]):
    parser = argparse.ArgumentParser(add_help=False)
    for var in vars:
        parser.add_argument(
            var.arg,
            type=var._type,
            help=var.description,
        )
    return parser

def run_notebook(notebook: str, notebook_args: t.List[str]):
    context = ICortexContext.from_file(notebook)

    vars = context.get_vars()

    parsed_args = get_notebook_arg_parser(vars).parse_args(notebook_args)

    scope = locals()

    for cell in context.iter_cells():
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
