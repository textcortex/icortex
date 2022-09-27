import os
import sys
import argparse
import toml
import click
from jupyter_console.app import ZMQTerminalIPythonApp
from icortex.services import service_dict, get_service
from icortex.config import DEFAULT_SERVICE, DEFAULT_ICORTEX_CONFIG_PATH
from icortex.install import is_kernel_installed, main as install_kernel
from icortex.kernel import ICortexKernel

# Jupyter devs did not make this easy
# TODO: Make less hacky
class ZMQTerminalICortexApp(ZMQTerminalIPythonApp):
    def parse_command_line(self, argv=None):
        argv = ["--kernel", "icortex"]
        super(ZMQTerminalIPythonApp, self).parse_command_line(argv)
        self.build_kernel_argv(self.extra_args)


def initialize_config(path: str):
    sorted_services = sorted(
        [key for key, val in service_dict.items() if not val.hidden]
    )
    sorted_services.remove(DEFAULT_SERVICE)
    sorted_services = [DEFAULT_SERVICE] + sorted_services

    service_name = click.prompt(
        "Which code generation service would you like to use?\nOptions: "
        + ", ".join(sorted_services)
        + "\nDefault",
        type=str,
        default=DEFAULT_SERVICE,
    )

    try:
        service = get_service(service_name)
    except KeyError:
        print(f"Service does not exist: {service_name}")
        quit()

    print(f"Selected service: {service_name}")
    skip_defaults = click.confirm("Use default options?", default=True)
    service_config = service.config_dialog(service, skip_defaults=skip_defaults)

    toml_dict = {"service": service_name, service_name: {}}
    for key, val in service_config.items():
        toml_dict[service_name][key] = val

    with open(path, "w") as f:
        toml.dump(toml_dict, f)


def get_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-i",
        "--init",
        action="store_true",
        help="Initialize ICortex configuration file in the current directory",
    )
    # parser.add_argument(
    #     "-c",
    #     "--config",
    #     type=str,
    #     help="Path to the configuration TOML file.",
    #     default=DEFAULT_ICORTEX_CONFIG_PATH,
    # )
    return parser


def read_config(path):
    return toml.load(open(path, "r"))


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    parser = get_parser()
    args = parser.parse_args(argv)

    # Install kernel if it's not already
    if not is_kernel_installed():
        install_kernel()

    # If no config file exists, initialize it
    # if args.init or not os.path.exists(args.config):
    #    initialize_config(args.config)
    if args.init or not os.path.exists(DEFAULT_ICORTEX_CONFIG_PATH):
        initialize_config(DEFAULT_ICORTEX_CONFIG_PATH)

    # print(ICortexKernel.config_path)
    # Launch shell
    if not args.init:
        ZMQTerminalICortexApp.launch_instance()


if __name__ == "__main__":
    main()
