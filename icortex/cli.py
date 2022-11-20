import os
import shlex
import sys
import argparse
from icortex.context import ICortexContext
from icortex.services import get_available_services
from icortex.defaults import DEFAULT_ICORTEX_CONFIG_PATH
from icortex.kernel.install import is_kernel_installed, main as install_kernel
from icortex.config import ICortexConfig


def get_parser(prog=None):
    service_names = get_available_services()
    parser = argparse.ArgumentParser(add_help=False)
    if prog is not None:
        parser.prog = prog

    subparsers = parser.add_subparsers(dest="command")

    ######################
    # Initialize ICortex #
    ######################

    # icortex init
    parser_init = subparsers.add_parser(
        "init",
        help="Initialize ICortex configuration in the current directory",
        add_help=False,
    )

    parser_init.add_argument(
        "--force", action="store_true", help="Force overwrite an existing configuration"
    )

    parser_init.add_argument(
        "--config",
        type=str,
        help="Path to the configuration TOML file.",
        default=DEFAULT_ICORTEX_CONFIG_PATH,
    )

    ##############################
    # Run a notebook as a script #
    ##############################

    # icortex run
    parser_run = subparsers.add_parser(
        "run",
        help="Run an ICortex notebook",
        add_help=False,
    )

    # Check whether the notebook exists
    parser_run.add_argument(
        "notebook",
        type=str,
        help="Path to the ICortex notebook to be run",
    )
    # A catch-all for the rest of the arguments
    parser_run.add_argument("notebook_args", nargs=argparse.REMAINDER)

    ########################################
    # Bake a notebook into a Python script #
    ########################################

    # icortex bake
    parser_bake = subparsers.add_parser(
        "bake",
        help="Bake an ICortex notebook into a Python script",
        add_help=False,
    )

    parser_bake.add_argument(
        "notebook",
        type=str,
        help="Path of the ICortex notebook to be run",
    )

    parser_bake.add_argument(
        "destination",
        type=str,
        help="Path of the destination Python file",
    )

    ##########################
    # Shell related commands #
    ##########################

    # icortex shell
    parser_shell = subparsers.add_parser(
        "shell",
        help="Start ICortex shell",
        add_help=False,
    )

    ########
    # Help #
    ########

    # icortex help
    parser_help = subparsers.add_parser(
        "help",
        help="Print help",
        add_help=False,
    )

    ############################
    # Service related commands #
    ############################

    # icortex service
    parser_service = subparsers.add_parser(
        "service",
        help="Set and configure code generation services",
        add_help=False,
    )
    parser_service_commands = parser_service.add_subparsers(
        dest="service_command",
        required=True,
    )

    # icortex service set <service_name>
    parser_service_commands_set = parser_service_commands.add_parser(
        "set",
        help="Set the service to be used for code generation",
        add_help=False,
    )
    parser_service_commands_set.add_argument(
        "service_name",
        choices=service_names,
        help="Name of the service to be used for code generation",
    )

    # icortex service show <service_name>
    parser_service_commands_show = parser_service_commands.add_parser(
        "show",
        help="Show current service",
        add_help=False,
    )

    # icortex service help
    parser_service_commands_help = parser_service_commands.add_parser(
        "help",
        help="Print help for the current service",
        add_help=False,
    )

    # icortex service set-var <variable_name> <variable_value>
    parser_service_commands_set_var = parser_service_commands.add_parser(
        "set-var",
        help="Set a variable for the current service",
        add_help=False,
    )
    parser_service_commands_set_var.add_argument(
        "variable_name",
        help="Name of the variable to be changed",
    )
    parser_service_commands_set_var.add_argument(
        "variable_value",
        type=str,
        help="New value for the variable",
    )

    # icortex service init <service_name>
    # Used to re-spawn the config dialog if some config for the service
    # already exists
    parser_service_commands_init = parser_service_commands.add_parser(
        "init",
        help="Initialize the configuration for the given service",
        add_help=False,
    )
    parser_service_commands_init.add_argument(
        "service_name",
        choices=service_names,
        help="Name of the service to be used for code generation",
    )
    if prog is not None:
        parser_init.prog = prog
        for action in parser._actions:
            if isinstance(action, argparse._SubParsersAction):
                for _, subparser in action.choices.items():
                    subparser.prog = prog

    return parser, parser_service


# def set_icortex_service(kernel, config_path=DEFAULT_ICORTEX_CONFIG_PATH):
#     if kernel is not None:
#         return ICortexConfig(DEFAULT_ICORTEX_CONFIG_PATH).set_service()
#     return False


def main(argv=None, prog=None, kernel=None):
    if argv is None:
        argv = sys.argv[1:]

    parser, parser_service = get_parser(prog=prog)
    args = parser.parse_args(argv)

    # Install kernel if it's not already
    if not is_kernel_installed():
        install_kernel()

    if "config" in args:
        config_path = args.config
    else:
        config_path = DEFAULT_ICORTEX_CONFIG_PATH

    config = ICortexConfig(config_path)

    if args.command == "init":
        # If no config file exists, initialize it
        if os.path.exists(config_path) and not args.force:
            print(f"The file {config_path} already exists. Use --force to overwrite.")
        else:
            config.init_config()
    elif args.command == "service":
        if args.service_command == "set":
            config.set_service_config(args.service_name)
        elif args.service_command == "set-var":
            config.set_service_var(args.variable_name, args.variable_value)
        elif args.service_command == "show":
            print(config.format_current_service())
        elif args.service_command == "init":
            config.set_service_config(args.service_name, hard_init=True)
        elif args.service_command == "help":
            parser_service.print_help()
    elif args.command == "help":
        parser.print_help()
    elif args.command == "run":
        context = ICortexContext.from_file(args.notebook)
        context.run(args.notebook_args)
    elif args.command == "bake":
        context = ICortexContext.from_file(args.notebook)
        context.bake(args.destination)
    elif args.command == "shell" or args.command is None:
        from icortex.kernel import get_icortex
        from icortex.kernel.app import ZMQTerminalICortexApp

        kernel = get_icortex()
        if kernel is None:
            ZMQTerminalICortexApp.launch_instance()
        else:
            # print("The ICortex shell is already running, skipping.")
            parser.print_help()


def eval_cli(prompt: str):
    argv = shlex.split(prompt)
    try:
        return main(argv=argv, prog=r"%icortex")
    except SystemExit:
        return


if __name__ == "__main__":
    main()
