import toml
from icortex.defaults import DEFAULT_SERVICE

from icortex.services import get_available_services, get_service
from icortex.helper import yes_no_input, prompt_input
from icortex.services.service_base import ServiceVariable


class ICortexConfig:
    def __init__(self, path: str):
        self.path = path
        self.read_config()
        self.kernel = None

    def set_kernel(self, kernel):
        self.kernel = kernel

    def get_service_name(self):
        if "service" in self.dict:
            return self.dict["service"]
        else:
            return None

    def set_service_var(self, var_name: str, var_value) -> bool:
        service_name = self.get_service_name()

        if service_name is None:
            print(
                "No service selected. Initialize a service by running `service init`."
            )
            return False

        try:
            service = get_service(service_name)
        except KeyError:
            print(f"Service does not exist: {service_name}")
            return False

        var: ServiceVariable = service.get_variable(service, var_name)

        if var is None:
            print(f"Variable {var_name} does not exist for service {service_name}.")
            return False

        # Type casting may be problematic with special types
        # Fix if that happens
        cast_value = var.type(var_value)
        self.dict[service_name][var_name] = cast_value

        success = self.write_config()
        if success:
            print(f"Set variable {var_name} to {cast_value}.")
            # kernel = get_icortex()
            if self.kernel is not None:
                self.set_service()
            return True
        else:
            raise Exception("Could not write configuration file")

    def set_service_config(self, service_name: str, hard_init=False) -> bool:
        try:
            service = get_service(service_name)
        except KeyError:
            print(f"Service does not exist: {service_name}")
            return False

        self.dict["service"] = service_name

        # Initialize service config if it's not already
        if not service_name in self.dict or hard_init:
            skip_defaults = yes_no_input("Use default variable values?", default=True)
            service_config = service.config_dialog(service, skip_defaults=skip_defaults)

            self.dict[service_name] = {}
            for key, val in service_config.items():
                self.dict[service_name][key] = val

        success = self.write_config()
        if success:
            print(f"Set service to {service_name} successfully.")
            # kernel = get_icortex()
            if self.kernel is not None:
                self.set_service()
            return True
        else:
            raise Exception("Could not write configuration file")

    def set_service(self):
        # TODO: pass the --config flag from icortex somehow
        # kernel = get_icortex()
        if self.kernel is None:
            return False

        if not self.dict:
            configure_now = yes_no_input(
                "ICortex is not configured. Would you like to configure it now?",
                default=True,
            )
            if configure_now:
                self.init_config()
                return self.set_service()
            else:
                return False

        # Initialize the Service object
        service_name = self.dict["service"]
        service_config = self.dict[service_name]
        service_class = get_service(service_name)

        self.kernel.set_service(service_class(**service_config))
        return True

    def ask_which_service(self) -> str:
        sorted_services = get_available_services()
        service_name = prompt_input(
            "Which code generation service would you like to use?\nAvailable services: "
            + ", ".join(sorted_services)
            + "\nDefault:",
            type=str,
            default=DEFAULT_SERVICE,
            press_enter=True,
        )
        return service_name

    def init_config(self):
        service_name = self.ask_which_service()
        return self.set_service_config(service_name)

    def read_config(self):
        try:
            self.dict = toml.load(open(self.path, "r"))
        except FileNotFoundError:
            self.dict = {}

    def write_config(self):
        with open(self.path, "w") as f:
            toml.dump(self.dict, f)
        return True

    def format_current_service(self):
        output_dict = {}
        if "service" in self.dict:
            service_name = self.dict["service"]
            output_dict["service"] = service_name
            if service_name in self.dict:
                output_dict[service_name] = self.dict[service_name]

        return toml.dumps(output_dict)
