import os
import sys
import argparse
import toml
from jupyter_console.app import ZMQTerminalIPythonApp
from icortex.services import get_available_services, get_service
from icortex.config import DEFAULT_SERVICE, DEFAULT_ICORTEX_CONFIG_PATH
from icortex.install import is_kernel_installed, main as install_kernel
from icortex.helper import prompt_input, yes_no_input

# from icortex.kernel import ICortexKernel

# Jupyter devs did not make this easy
# TODO: Make less hacky
class ZMQTerminalICortexApp(ZMQTerminalIPythonApp):
    def parse_command_line(self, argv=None):
        argv = ["--kernel", "icortex"]
        super(ZMQTerminalIPythonApp, self).parse_command_line(argv)
        self.build_kernel_argv(self.extra_args)


def ask_which_service() -> str:
    sorted_services = get_available_services()
    service_name = prompt_input(
        "Which code generation service would you like to use?\nOptions: "
        + ", ".join(sorted_services)
        + "\nDefault",
        type=str,
        default=DEFAULT_SERVICE,
    )
    return service_name


def init_config(path: str):
    service_name = ask_which_service()
    return set_service(path, service_name)


def set_service(path, service_name):
    try:
        service = get_service(service_name)
    except KeyError:
        print(f"Service does not exist: {service_name}")
        return False

    print(f"Selected service: {service_name}")

    dict = read_config(path)
    dict["service"] = service_name

    if not service_name in dict:
        skip_defaults = yes_no_input("Use default options?", default=True)
        service_config = service.config_dialog(service, skip_defaults=skip_defaults)

        dict[service_name] = {}
        for key, val in service_config.items():
            dict[service_name][key] = val

    success = write_config(path, dict)
    if success:
        print(f"Initialized service {service_name} successfully.")
        return True
    else:
        raise Exception("Could not write configuration file")


def get_parser():
    # parser = argparse.ArgumentParser()

    # parser.add_argument(
    #     "-c",
    #     "--config",
    #     type=str,
    #     help="Path to the configuration TOML file.",
    #     default=DEFAULT_ICORTEX_CONFIG_PATH,
    # )

    service_names = get_available_services()
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    parser_init = subparsers.add_parser(
        "init", help="Initialize ICortex in the current directory"
    )
    parser_init.add_argument(
        "--force", action="store_true", help="Force overwrite an existing configuration"
    )

    parser_shell = subparsers.add_parser("shell", help="Start ICortex shell")

    parser_service = subparsers.add_parser(
        "service", help="Set and configure code generation services"
    )
    parser_service_commands = parser_service.add_subparsers(
        dest="service_command",
    )

    parser_service_commands_set = parser_service_commands.add_parser(
        "set", help="Set the service to be used for code generation"
    )
    parser_service_commands_init = parser_service_commands.add_parser(
        "init", help="Initialize the configuration for the given service"
    )
    parser_service_commands_set.add_argument(
        "service_name",
        choices=service_names,
        help="Name of the service to be used for code generation",
    )

    return parser


def service_cli(args):
    if args.service_command == "set":
        set_service(DEFAULT_ICORTEX_CONFIG_PATH, args.service_name)
    elif args.service_command == "init":
        init_config(DEFAULT_ICORTEX_CONFIG_PATH)


def read_config(path):
    try:
        return toml.load(open(path, "r"))
    except FileNotFoundError:
        return {}


def write_config(path: str, dict):
    with open(path, "w") as f:
        toml.dump(dict, f)
    return True


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    parser = get_parser()
    args = parser.parse_args(argv)
    print(args)

    # Install kernel if it's not already
    if not is_kernel_installed():
        install_kernel()

    # If no config file exists, initialize it
    if args.command == "init":
        if os.path.exists(DEFAULT_ICORTEX_CONFIG_PATH) and not args.force:
            print(
                f"The file {DEFAULT_ICORTEX_CONFIG_PATH} already exists. Use --force to overwrite."
            )
            quit(1)
        else:
            init_config(DEFAULT_ICORTEX_CONFIG_PATH)

    if args.command == "service":
        service_cli(args)

    # if args.init or not os.path.exists(DEFAULT_ICORTEX_CONFIG_PATH):
    # init_service(DEFAULT_ICORTEX_CONFIG_PATH)

    # Launch shell
    if args.command == "shell" or args.command is None:
        ZMQTerminalICortexApp.launch_instance()


if __name__ == "__main__":
    main()
