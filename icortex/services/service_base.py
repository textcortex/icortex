import os
import argparse
import json
import typing as t
from abc import ABC, abstractclassmethod

from icortex.defaults import (
    DEFAULT_AUTO_EXECUTE,
    DEFAULT_AUTO_INSTALL_PACKAGES,
    DEFAULT_CACHE_PATH,
    DEFAULT_QUIET,
)
from icortex.context import ICortexContext
from icortex.helper import escape_quotes, highlight_python, prompt_input, yes_no_input
from icortex.pypi import get_missing_modules, install_missing_packages
from icortex.services.generation_result import GenerationResult
from icortex.services.service_interaction import ServiceInteraction
from icortex.parser import lex_prompt

def is_str_repr(s: str):
    quotes = ["'", '"']
    return len(s) >= 2 and s[0] in quotes and s[-1] in quotes


class ServiceVariable:
    """A variable for a code generation service

    Args:
        type_ (Any): Variable type.
        default (Any, optional): Default value, should match :data:`type_`.
        help (str, optional): Help string for the variable. Defaults to "".
        secret (bool, optional): When set to
            True, the variable is omitted from caches and the context. Defaults to False.
        argparse_args (List, optional): Args to
            be given to :func:`ArgumentParser.add_argument`. Defaults to [].
        argparse_kwargs (Dict, optional): Keywords args to
            be given to :func:`ArgumentParser.add_argument`. Defaults to {}.
        require_arg (bool, optional): When set to true,
            the prompt parser will raise an error if the variable is not specified.
            Defaults to False.
    """

    def __init__(
        self,
        type_: type,
        default: t.Any = None,
        help: str = "",
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
    """Abstract base class for interfacing a code generation service.
    Its main purpose is to provide a flexible API for connecting user
    prompts with whatever logic the service
    provider might choose to implement. User prompts adhere to
    POSIX argument syntax and are parsed with
    `argparse <https://docs.python.org/3/library/argparse.html>`__.

    To create a new service:

    - Assign a unique name to :attr:`name`
    - Add your class to the dict :data:`icortex.services.AVAILABLE_SERVICES`.
      Use :attr:`name` as the key and don't forget to include module information.
    - Determine the parameters that the service will use for code generation and add
      them to :attr:`variables`.
    - Implement :func:`generate`.

    Check out :class:`icortex.services.textcortex.TextCortexService` as a
    reference implementation.

    Attributes
    ----------
    variables: Dict[str, ServiceVariable]
        A dict that maps variable names to :class:`ServiceVariable` s.
    name: str
        A unique name.
    description: str
        Description string.
    prompt_parser: argparse.ArgumentParser
        Parser to parse the prompts.
    """

    name: str = "base"
    description: str = "Base class for a code generation service"
    # Each child class will need to add their specific arguments
    # by extending `variables`
    variables: t.Dict[str, ServiceVariable] = {}
    # This has stopped working, fix
    hidden: bool = False

    def __init__(self, **kwargs: t.Dict[str, t.Any]):
        """Classes that derive from ServiceBase are always initialized with
        keyword arguments that contain values for the service variables.
        The values can come
        """
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
            required=DEFAULT_AUTO_EXECUTE,
            help="Execute the Python code returned by TextCortex API directly.",
        )
        self.prompt_parser.add_argument(
            "-r",
            "--regenerate",
            action="store_true",
            required=False,
            help="Make the kernel ignore cached responses and make a new request to TextCortex API.",
        )
        self.prompt_parser.add_argument(
            "-p",
            "--auto-install-packages",
            action="store_true",
            required=DEFAULT_AUTO_INSTALL_PACKAGES,
            help="Auto-install packages that are imported in the generated code but missing in the active Python environment.",
        )
        self.prompt_parser.usage = (
            "%%prompt your prompt goes here [-e] [-r] [-p] ..."
        )

        self.prompt_parser.description = self.description

        # Add service-specific variables
        for key, var in self.variables.items():
            # If user has specified a value for the variable, use that
            # Otherwise, the default value will be used
            if key in kwargs:
                var.set_default(kwargs[key])

            # Omit secret arguments from the parser, but still read them
            if var.secret == False and len(var.argparse_args) > 0:
                self.prompt_parser.add_argument(
                    *var.argparse_args,
                    **var.argparse_kwargs,
                )

    def find_cached_interaction(
        self,
        request_dict: t.Dict,
        cache_path: str = DEFAULT_CACHE_PATH,
    ) -> ServiceInteraction:
        cache = self._read_cache(cache_path)
        # If the the same request is found in the cache, return the cached response
        # Return the latest found response by default
        for dict_ in reversed(cache):
            interaction = ServiceInteraction.from_dict(dict_)
            if interaction.generation_result.request_dict == request_dict:
                return interaction
        return None

    def cache_interaction(
        self,
        interaction: ServiceInteraction,
        cache_path: str = DEFAULT_CACHE_PATH,
    ):
        cache = self._read_cache(DEFAULT_CACHE_PATH)
        cache.append(interaction.to_dict())
        return self._write_cache(cache, cache_path)

    @abstractclassmethod
    def generate(
        self,
        prompt: str,
        args,
        context: ICortexContext = None,
    ) -> GenerationResult:
        """Implement the logic that generates code from user prompts here.

        Args:
            prompt (str): The prompt that describes what the generated code should perform
            context (Dict[str, Any], optional): A dict containing the current notebook
                context, that is in the Jupyter notebook format.
                See :class:`icortex.context.ICortexHistory` for more details.

        Returns:
            List[Dict[Any, Any]]: A list that contains code generation results. Should ideally be valid Python code.
        """
        raise NotImplementedError

    @abstractclassmethod
    def get_outputs_from_result(
        self, generation_result: GenerationResult
    ) -> t.List[str]:
        """Given a GenerationResult, return a dict that contains the response.

        Args:
            generation_result (GenerationResult): The result of the generation

        Returns:
            Dict[str, Any]: The response dict
        """
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

    def get_variable(self, var_name: str) -> ServiceVariable:
        """Get a variable by its name

        Args:
            var_name (str): Name of the variable

        Returns:
            ServiceVariable: Requested variable
        """
        for key, var in self.variables.items():
            if key == var_name:
                return var
        return None

    def get_variable_names(self) -> t.List[str]:
        """Get a list of variable names.

        Returns:
            List[str]: List of variable names
        """
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

    def eval_prompt(self, raw_prompt: str, context) -> ServiceInteraction:
        # Print help if the user has typed `/help`
        argv = lex_prompt(raw_prompt)
        args = self.prompt_parser.parse_args(argv)

        args.prompt = " ".join(args.prompt)

        # Otherwise, generate with the prompt
        generation_result = self.generate(
            args.prompt,
            args,
            context=context,
        )
        outputs = self.get_outputs_from_result(generation_result)

        # TODO: Account for multiple response values
        code_ = outputs[0]

        # Print the generated code
        print(highlight_python(code_))

        # Search for any missing modules
        missing_modules = get_missing_modules(code_)

        install_packages_yesno = False
        if len(missing_modules) > 0 and not args.auto_install_packages:
            install_packages_yesno = yes_no_input(
                f"The following modules are missing in your environment: {', '.join(missing_modules)}\nAttempt to find and install corresponding PyPI packages?"
            )
        install_packages = args.auto_install_packages or install_packages_yesno

        unresolved_modules = []
        if install_packages:
            # Unresolved modules are modules that cannot be mapped
            # to any PyPI packages according to the local data in this library
            unresolved_modules = install_missing_packages(code_)
            if len(unresolved_modules) > 0:
                print(
                    f"""The following imported modules could not be resolved to PyPI packages: {', '.join(unresolved_modules)}
        Install them manually and try again.
        """
                )

        # Modules that are still missing regardless of
        # whether the user tried to auto-install them or not:
        still_missing_modules = get_missing_modules(code_)

        execute_yesno = False
        if not args.execute and len(still_missing_modules) == 0:
            execute_yesno = yes_no_input("Proceed to execute?")

        execute = args.execute or execute_yesno

        if execute and len(still_missing_modules) > 0:
            execute = False
            if args.auto_install_packages:
                bermuda_modules = [
                    module
                    for module in still_missing_modules
                    if module not in unresolved_modules
                ]
                print(
                    f"""These modules should have been installed at this point, but they are still missing:  {', '.join(bermuda_modules)}
    This might be due to an installer issue, please resolve manually.""",
                )
            print(
                f"Skipping execution due to missing modules: {', '.join(still_missing_modules)}."
            )

        ret = ServiceInteraction(
            name=self.name,
            args=args.__dict__,
            generation_result=generation_result,
            execute=execute,
            outputs=[code_],
            install_packages=install_packages,
            missing_modules=missing_modules,
        )
        self.cache_interaction(ret, cache_path=DEFAULT_CACHE_PATH)
        return ret
