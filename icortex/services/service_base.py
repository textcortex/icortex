import os
import argparse
import json
import typing as t
from abc import ABC, abstractmethod

from icortex.defaults import DEFAULT_CACHE_PATH
from icortex.helper import prompt_input


def is_str_repr(s: str):
    quotes = ["'", '"']
    return len(s) >= 2 and s[0] in quotes and s[-1] in quotes


class ServiceVariable:
    def __init__(
        self,
        type_: t.Any,
        default: t.Any = None,
        help: str = None,
        secret: bool = False,
        argparse_args: t.List = [],
        argparse_kwargs: t.Dict = {},
        require_arg: bool = False,
    ):
        self.argparse_args = [*argparse_args]
        self.argparse_kwargs = {**argparse_kwargs}
        self.type = type_
        self.help = help
        self.set_default(default)
        self.set_help(help)
        self.secret = secret
        self.require_arg = require_arg
        if require_arg:
            self.argparse_kwargs["required"] = True
        if self.type is not None:
            self.argparse_kwargs["type"] = self.type

    def set_default(self, val):
        if val is None:
            self.default = None
            return
        assert isinstance(val, self.type)
        self.default = val
        self.argparse_kwargs["default"] = val
        # Update the help string
        self.set_help(self.help)

    def set_help(self, help: str):
        if help is not None:
            help_str = help
            if self.default is not None:
                help_str += f" Default: {repr(self.default)}"
            self.argparse_kwargs["help"] = help_str
        else:
            self.help = None


class ServiceBase(ABC):
    name: str = "base"
    description: str = "Base class for a code generation service"
    # Each child class will need to add their specific arguments
    # by extending `variables`
    variables: t.Dict[str, ServiceVariable] = {}
    hidden: bool = False

    def __init__(self, config: t.Dict):
        # Create the prompt parser and add default arguments
        self.prompt_parser = argparse.ArgumentParser(
            add_help=False,
        )
        self.prompt_parser.add_argument(
            "prompt",
            nargs="*",
            type=str,
            help="The prompt that describes what the generated Python code should perform.",
        )
        self.prompt_parser.add_argument(
            "-e",
            "--execute",
            action="store_true",
            required=False,
            help="Execute the Python code returned by the TextCortex API in the same cell.",
        )
        self.prompt_parser.add_argument(
            "-r",
            "--regenerate",
            action="store_true",
            required=False,
            help="Make the kernel ignore cached responses and makes a new request to the TextCortex API.",
        )
        self.prompt_parser.add_argument(
            "-i",
            "--include-history",
            action="store_true",
            required=False,
            help="Submit notebook history along with the prompt.",
        )
        self.prompt_parser.add_argument(
            "-p",
            "--auto-install-packages",
            action="store_true",
            required=False,
            help="Auto-install packages that are imported in the generated code but missing in the active Python environment.",
        )
        self.prompt_parser.add_argument(
            "-o",
            "--nonint",
            action="store_true",
            required=False,
            help=f"Non-interactive, do not ask any questions.",
        )
        self.prompt_parser.add_argument(
            "-q",
            "--quiet",
            action="store_true",
            required=False,
            help="Do not print the generated code.",
        )
        self.prompt_parser.usage = "%p your prompt goes here [-e] [-r] [-i] [-p] ..."

        self.prompt_parser.description = self.description

        # Add service-specific variables
        for key, var in self.variables.items():
            # If user has specified a value for the variable, use that
            # Otherwise, the default value will be used
            if key in config:
                var.set_default(config[key])

            # Omit secret arguments from the parser, but still read them
            if var.secret == False and len(var.argparse_args) > 0:
                self.prompt_parser.add_argument(
                    *var.argparse_args,
                    **var.argparse_kwargs,
                )

    def find_cached_response(
        self,
        request_dict: t.Dict,
        cache_path: str = DEFAULT_CACHE_PATH,
    ):
        cache = self._read_cache(cache_path)
        # If the the same request is found in the cache, return the cached response
        # Return the latest found response by default
        for dict_ in reversed(cache):
            if dict_["request"] == request_dict:
                return dict_["response"]
        return None

    def cache_response(
        self,
        request_dict: t.Dict,
        response_dict: t.Dict,
        cache_path: str = DEFAULT_CACHE_PATH,
    ):
        cache = self._read_cache(DEFAULT_CACHE_PATH)
        cache.append({"request": request_dict, "response": response_dict})
        return self._write_cache(cache, cache_path)

    @abstractmethod
    def generate(self, prompt: str, context: t.Dict[str, t.Any] = {}):
        raise NotImplementedError

    def config_dialog(self, skip_defaults=False):
        return_dict = {}
        for key, var in self.variables.items():
            if isinstance(var, ServiceVariable):
                if skip_defaults and var.default is not None:
                    user_val = var.default
                else:
                    kwargs = {"type": var.type}
                    if var.default is not None:
                        kwargs["default"] = repr(var.default)
                    if var.help is not None:
                        prompt = f"{key} ({var.help})"
                    else:
                        prompt = f"{key}"
                    user_val = prompt_input(prompt, **kwargs)
                    # If the input is a string representation, evaluate it
                    # This is for when the user wants to type in a string with escape characters
                    if var.type == str and is_str_repr(user_val):
                        user_val = eval(user_val)
            else:
                raise ValueError(f"Dict entry is not ServiceVariable: {var}")

            return_dict[key] = user_val
        return return_dict

    def get_variable(self, var_name: str):
        for key, var in self.variables.items():
            if key == var_name:
                return var
        return None

    def get_variable_names(self):
        return [var.name for var in self.variables]

    def _read_cache(self, cache_path):
        # Check whether the cache file already exists
        if os.path.exists(cache_path):
            try:
                with open(cache_path, "r") as f:
                    cache = json.load(f)
            except json.decoder.JSONDecodeError:
                cache = []
        else:
            cache = []
        return cache

    def _write_cache(self, cache: t.List[t.Dict], cache_path):
        with open(cache_path, "w") as f:
            json.dump(cache, f, indent=2)
        return True
