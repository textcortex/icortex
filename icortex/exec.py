import shlex

from pygments import highlight
from pygments.formatters import Terminal256Formatter
from pygments.lexers import PythonLexer

from icortex.pypi import install_missing_packages, get_missing_modules
from icortex.kernel import get_icortex_kernel
from icortex.helper import yes_no_input
from icortex.config import *


def highlight_python(code: str):
    return highlight(code, PythonLexer(), Terminal256Formatter())


def run_dialog(
    code: str,
    execute: bool = False,
    auto_install_packages: bool = DEFAULT_AUTO_INSTALL_PACKAGES,
    quiet: bool = DEFAULT_QUIET,
    nonint: bool = False,
):
    if not quiet:
        print(highlight_python(code))

    missing_modules = get_missing_modules(code)

    if len(missing_modules) > 0 and not auto_install_packages and not nonint:
        auto_install_packages = yes_no_input(
            f"The following modules are missing in your environment: {', '.join(missing_modules)}\nAttempt to find and install corresponding PyPI packages?"
        )

    unresolved_modules = []
    if auto_install_packages:
        # Unresolved modules are modules that cannot be mapped
        # to any PyPI packages according to the local data in this library
        unresolved_modules = install_missing_packages(code)
        if len(unresolved_modules) > 0:
            print(
                f"""The following imported modules could not be resolved to PyPI packages: {', '.join(unresolved_modules)}
    Install them manually and try again.
    """
            )
            return ""

    # Modules that are still missing regardless of
    # whether the user tried to auto-install them or not:
    still_missing_modules = get_missing_modules(code)

    if not execute and not nonint and len(still_missing_modules) == 0:
        execute = yes_no_input("Proceed to execute?")

    if execute and len(still_missing_modules) == 0:
        # return exec(code)
        return code
    elif execute and len(still_missing_modules) > 0:
        if auto_install_packages:
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
    return ""


def eval_prompt(prompt_with_args: str):
    service = get_icortex_kernel().service

    # Print help if the user has typed `/help`
    argv = shlex.split(prompt_with_args)
    args = service.prompt_parser.parse_args(argv)
    prompt = " ".join(args.prompt)
    if prompt == "help":
        return "from icortex import print_help\nprint_help()"

    # Otherwise, generate with the prompt
    response = service.generate(prompt_with_args)
    # TODO: Account for multiple response values
    code_: str = response[0]["text"]

    return run_dialog(
        code_,
        execute=args.execute,
        auto_install_packages=args.auto_install_packages,
        quiet=args.quiet,
        nonint=args.nonint,
    )
