import argparse
import typing as t

from icortex.helper import escape_quotes

VAR_NAME_PREFIX = "_"

TYPE_STR_TO_TYPE = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
    # "list": list,
    # "dict": dict,
    # "tuple": tuple,
    # "set": set,
}

class Var:
    def __init__(self, arg, name, value, type, description=None):
        self.arg = arg
        self.name = name
        self.value = value
        # TODO: Rename to type_str
        self.type = type
        self.description = description

        self._type = TYPE_STR_TO_TYPE[type]

    def from_var_magic(line):
        args = get_var_magic_parser().parse_args(line.split())
        var_name = VAR_NAME_PREFIX + args.name
        value = parse_var(args.value, args.type)
        return Var(args.name, var_name, value, args.type, args.description)

    def get_code(self):
        "Get code that assigns the variable value"
        code = f"{self.name} = {repr(self.value)}\n"
        code += f"{self.name}"  # For showing in the output
        return code

    def to_dict(self):
        "Convert to a dictionary"
        ret = {
            "arg": self.arg,
            "name": self.name,
            "value": self.value,
            "type": self.type,
        }
        if self.description:
            ret["description"] = self.description
        return ret

    def from_dict(d: t.Dict[str, t.Any]):
        "Create a Var from a dictionary"
        return Var(
            d["arg"], d["name"], d["value"], d["type"], d.get("description", None)
        )

    def __repr__(self):
        return f"Var({self.arg}={repr(self.value)})"


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
    parser.add_argument(
        "--description",
        type=str,
        help="Description of the variable to be set",
    )
    return parser


def parse_var(val: str, type: str):
    if type == "str":
        return val
    elif type == "int":
        return int(val)
    elif type == "float":
        return float(val)
    elif type == "bool":
        return bool(val)
    else:
        raise ValueError(f"Unknown type: {type}")


# def escape_var(val):
#     if type == "str":
#         if "\n" in val:
#             return f'"""{escape_quotes(val)}"""'
#         else:
#             return f'"{escape_quotes(val)}"'
#     elif type == "int":
#         return str(int(val))
#     elif type == "float":
#         return str(float(val))
#     elif type == "bool":
#         return str(bool(val))
#     else:
#         raise ValueError(f"Unknown type: {type}")
