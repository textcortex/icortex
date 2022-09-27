import os
import argparse
import json
import click

from icortex.config import *

import typing as t


def is_str_repr(s: str):
    quotes = ["'", '"']
    return len(s) >= 2 and s[0] in quotes and s[-1] in quotes


class ServiceOption:
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
        self.type = type_
        self.default = default  # Default value
        self.help = help
        self.argparse_args = [*argparse_args]
        self.argparse_kwargs = {**argparse_kwargs}
        self.secret = secret
        self.require_arg = require_arg
        if require_arg:
            self.argparse_kwargs["required"] = True
        if self.help is not None:
            help_str = self.help
            if self.default is not None:
                help_str += f" Default: {repr(self.default)}"
            self.argparse_kwargs["help"] = help_str
        if self.default is not None:
            assert isinstance(default, type_)
            self.argparse_kwargs["default"] = self.default


class ServiceBase:
    name: str = "base"
    description: str = "Base class for a code generation service"
    # Each child class will need to add their specific arguments
    # by extending `options`
    options: t.Dict[str, ServiceOption] = {}
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
        self.prompt_parser.usage = "/your prompt goes here [-e] [-r] [-i] [-p] ..."

        self.prompt_parser.description = self.description

        # Add service-specific options
        for key, opt in self.options.items():
            # If user has specified a value for the option, use that
            # Otherwise, the default value will be used
            if key in config:
                opt.default = config[key]

            # Omit secret arguments from the parser, but still read them
            if opt.secret == False and len(opt.argparse_args) > 0:
                self.prompt_parser.add_argument(
                    *opt.argparse_args,
                    **opt.argparse_kwargs,
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

    def generate(self, prompt: str):
        raise NotImplementedError

    def config_dialog(self, skip_defaults=False):
        return_dict = {}
        for key, opt in self.options.items():
            if isinstance(opt, ServiceOption):
                if skip_defaults and opt.default is not None:
                    user_val = opt.default
                else:
                    kwargs = {"type": opt.type}
                    if opt.default is not None:
                        kwargs["default"] = repr(opt.default)
                    if opt.help is not None:
                        prompt = f"{key} ({opt.help})"
                    else:
                        prompt = f"{key}"
                    user_val = click.prompt(prompt, **kwargs)
                    # If the input is a string representation, evaluate it
                    # This is for when the user wants to type in a string with escape characters
                    if opt.type == str and is_str_repr(user_val):
                        user_val = eval(user_val)
            else:
                raise ValueError(f"Dict entry is not ServiceOption: {opt}")

            return_dict[key] = user_val
        return return_dict

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
