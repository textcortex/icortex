import os
import shlex
import sys
import argparse
from icortex.kernel import get_icortex_kernel
from jupyter_console.app import ZMQTerminalIPythonApp
from icortex.services import get_available_services
from icortex.defaults import DEFAULT_ICORTEX_CONFIG_PATH
from icortex.install import is_kernel_installed, main as install_kernel
from icortex.config import ICortexConfig

# Jupyter devs did not make this easy
# TODO: Make less hacky
class ZMQTerminalICortexApp(ZMQTerminalIPythonApp):
    def parse_command_line(self, argv=None):
        argv = ["--kernel", "icortex"]
        super(ZMQTerminalIPythonApp, self).parse_command_line(argv)
        self.build_kernel_argv(self.extra_args)


def get_parser(prog=None):
    service_names = get_available_services()
    parser = argparse.ArgumentParser()
    if prog is not None:
        parser.prog = prog

    subparsers = parser.add_subparsers(dest="command")

    ######################
    # Initialize ICortex #
    ######################

    # //init
    parser_init = subparsers.add_parser(
        "init", help="Initialize ICortex configuration in the current directory"
    )

    # parser.add_argument(
    #     "-c",
    #     "--config",
    #     type=str,
    #     help="Path to the configuration TOML file.",
    #     default=DEFAULT_ICORTEX_CONFIG_PATH,
    # )

    parser_init.add_argument(
        "--force", action="store_true", help="Force overwrite an existing configuration"
    )

    ##########################
    # Shell related commands #
    ##########################

    # //shell
    parser_shell = subparsers.add_parser("shell", help="Start ICortex shell")

    ############################
    # Service related commands #
    ############################

    # //service
    parser_service = subparsers.add_parser(
        "service", help="Set and configure code generation services"
    )
    parser_service_commands = parser_service.add_subparsers(
        dest="service_command",
        required=True,
    )

    # //service set <service_name>
    parser_service_commands_set = parser_service_commands.add_parser(
        "set", help="Set the service to be used for code generation"
    )
    parser_service_commands_set.add_argument(
        "service_name",
        choices=service_names,
        help="Name of the service to be used for code generation",
    )

    # //service show <service_name>
    parser_service_commands_show = parser_service_commands.add_parser(
        "show", help="Show current service"
    )

    # //service set-var <variable_name> <variable_value>
    parser_service_commands_set_var = parser_service_commands.add_parser(
        "set-var", help="Set a variable for the current service"
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

    # //service init <service_name>
    # Used to re-spawn the config dialog if some config for the service
    # already exists
    parser_service_commands_init = parser_service_commands.add_parser(
        "init", help="Initialize the configuration for the given service"
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

    return parser


def service_cli(args):
    if args.service_command == "set":
        ICortexConfig(DEFAULT_ICORTEX_CONFIG_PATH).set_service_config(args.service_name)
    if args.service_command == "set-var":
        ICortexConfig(DEFAULT_ICORTEX_CONFIG_PATH).set_service_var(
            args.variable_name, args.variable_value
        )
    if args.service_command == "show":
        print(ICortexConfig(DEFAULT_ICORTEX_CONFIG_PATH).format_current_service())
    elif args.service_command == "init":
        ICortexConfig(DEFAULT_ICORTEX_CONFIG_PATH).set_service_config(
            args.service_name, hard_init=True
        )


def set_icortex_service(config_path=DEFAULT_ICORTEX_CONFIG_PATH):
    kernel = get_icortex_kernel()
    if kernel is not None:
        return ICortexConfig(DEFAULT_ICORTEX_CONFIG_PATH).set_service()
    return False


def main(argv=None, prog=None):
    if argv is None:
        argv = sys.argv[1:]

    parser = get_parser(prog=prog)
    # if prog is not None:
    #     parser.prog = prog

    args = parser.parse_args(argv)

    # Install kernel if it's not already
    if not is_kernel_installed():
        install_kernel()

    # If no config file exists, initialize it
    if args.command == "init":
        if os.path.exists(DEFAULT_ICORTEX_CONFIG_PATH) and not args.force:
            print(
                f"The file {DEFAULT_ICORTEX_CONFIG_PATH} already exists. Use --force to overwrite."
            )
        else:
            ICortexConfig(DEFAULT_ICORTEX_CONFIG_PATH).init_config()

    if args.command == "service":
        service_cli(args)

    # if args.init or not os.path.exists(DEFAULT_ICORTEX_CONFIG_PATH):
    # init_service(DEFAULT_ICORTEX_CONFIG_PATH)

    # Launch shell
    if args.command == "shell" or args.command is None:
        kernel = get_icortex_kernel()
        if kernel is None:
            ZMQTerminalICortexApp.launch_instance()
        else:
            print("The ICortex shell is already running, skipping.")


def eval_cli(prompt: str):
    argv = shlex.split(prompt)
    try:
        return main(argv=argv, prog="//")
    except SystemExit:
        return


if __name__ == "__main__":
    main()
