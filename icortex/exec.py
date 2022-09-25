import shlex
import toml

from pygments import highlight
from pygments.formatters import Terminal256Formatter
from pygments.lexers import PythonLexer

from .service import get_service
from .pypi import install_missing_packages, get_missing_modules
from .config import *


def is_prompt(input: str):
    return input.strip()[0] == "/"


def extract_prompt(input: str):
    return input.strip()[1:].strip()


def yes_no_input(message: str, default_no=False):
    if not default_no:
        message += " [Y/n]"
    else:
        message += " [y/N]"

    print(message)
    user_input = input()

    return (user_input == "" and not default_no) or user_input.strip().lower() == "y"


def highlight_python(code: str):
    return highlight(code, PythonLexer(), Terminal256Formatter())


def execute_interactive(
    code: str,
    execute: bool = False,
    auto_install_packages: bool = DEFAULT_AUTO_INSTALL_PACKAGES,
    hide_code: bool = DEFAULT_HIDE_CODE,
    nonint: bool = False,
):
    if not hide_code:
        print(highlight_python(code))

    # Missing modules are modules that are still missing regardless of
    # whether the user tried to auto-install them or not
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
            return

    # Missing modules are modules that are still missing regardless of
    # whether the user tried to auto-install them or not
    still_missing_modules = get_missing_modules(code)

    if not execute and not nonint and len(still_missing_modules) == 0:
        execute = yes_no_input("Proceed to execute?")

    if execute and len(still_missing_modules) == 0:
        exec(code)
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
    return


def eval_prompt(prompt_with_args: str):
    # Read ICortex config every time a prompt is evaluated
    try:
        icortex_config = toml.load(DEFAULT_ICORTEX_CONFIG_PATH)
    except FileNotFoundError:
        # If config file doesn't exist, default to TextCortex
        icortex_config = {"service": "textcortex", "textcortex": {}}

    # Initialize the Service object
    service_name = icortex_config["service"]
    service_config = icortex_config[service_name]
    service_class = get_service(service_name)
    service = service_class(service_config)

    # Print help if the user has typed `/help`
    argv = shlex.split(prompt_with_args)
    args = service.prompt_parser.parse_args(argv)
    prompt = " ".join(args.prompt)
    if prompt == "help":
        service.prompt_parser.print_help()
        return

    # Otherwise, generate with the prompt
    response = service.generate(prompt_with_args)
    # TODO: Account for multiple response values
    code_: str = response[0]["text"]

    execute_interactive(
        code_,
        execute=args.execute,
        auto_install_packages=args.auto_install_packages,
        hide_code=args.hide_code,
        nonint=args.nonint,
    )
