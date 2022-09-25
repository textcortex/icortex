import os
import argparse
import toml
import click
from icortex.service import service_dict, get_service
from icortex.config import DEFAULT_SERVICE, DEFAULT_ICORTEX_CONFIG_PATH


def initialize_config(path):
    sorted_services = sorted(service_dict.keys())
    sorted_services.remove(DEFAULT_SERVICE)
    sorted_services = [DEFAULT_SERVICE] + sorted_services

    service_name = click.prompt(
        "Which code generation service would you like to use? Options: "
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


parser = argparse.ArgumentParser()

parser.add_argument(
    "-i",
    "--init",
    action="store_true",
    help="Initialize ICortex configuration file in the current directory",
)
parser.add_argument(
    "-c",
    "--config",
    type=str,
    help="Path to the configuration TOML file.",
    default=DEFAULT_ICORTEX_CONFIG_PATH,
)


def main():
    args = parser.parse_args()
    if args.init or not os.path.exists(args.config):
        initialize_config(args.config)


if __name__ == "__main__":
    main()
