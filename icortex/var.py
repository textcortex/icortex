import argparse

from icortex.helper import escape_quotes

VAR_NAME_PREFIX = "_"


def get_var_magic_parser():
    parser = argparse.ArgumentParser(
        add_help=False,
    )
    parser.add_argument(
        "name",
        type=str,
        help="Name of the variable to be set",
    )
    parser.add_argument(
        "value",
        type=str,
        help="Value of the variable to be set",
    )
    parser.add_argument(
        "--type",
        choices=[
            "int",
            "float",
            "str",
            "bool",
        ],  # TODO: Add more types, e.g. list, dict, etc.
        default="str",
        help="Type of the variable to be set",
    )
    return parser


def format_var(val, type):
    if type == "str":
        if "\n" in val:
            return f'"""{escape_quotes(val)}"""'
        else:
            return f'"{escape_quotes(val)}"'
    elif type == "int":
        return str(int(val))
    elif type == "float":
        return str(float(val))
    elif type == "bool":
        return str(bool(val))
    else:
        raise ValueError(f"Unknown type: {type}")


def line_to_code(line):
    "Convert var magic line to code that assigns the variable value"
    args = get_var_magic_parser().parse_args(line.split())
    var_name = VAR_NAME_PREFIX + args.name
    value = format_var(args.value, args.type)
    code = f"{var_name} = {value}\n"
    code += f"{var_name}" # For showing in the output
    return code
