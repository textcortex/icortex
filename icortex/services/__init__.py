import typing as t
from copy import deepcopy
import importlib

from icortex.services.service_base import ServiceBase, ServiceVariable

from icortex.defaults import (
    DEFAULT_AUTO_EXECUTE,
    DEFAULT_AUTO_INSTALL_PACKAGES,
    DEFAULT_QUIET,
    DEFAULT_SERVICE,
)

service_dict = {
    "echo": "icortex.services.echo.EchoService",
    "textcortex": "icortex.services.textcortex.TextCortexService",
    "openai": "icortex.services.openai.OpenAIService",
    "huggingface": "icortex.services.huggingface.HuggingFaceAutoService",
}


def get_service(name: str) -> t.Type[ServiceBase]:
    path = service_dict[name]
    module_path, service_name = path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    service = module.__dict__[service_name]
    return service


def get_available_services() -> t.List[str]:
    # sorted_services = sorted(
    #     [key for key, val in service_dict.items() if not val.hidden]
    # )
    sorted_services = list(sorted(service_dict.keys()))
    sorted_services.remove(DEFAULT_SERVICE)
    sorted_services = [DEFAULT_SERVICE] + sorted_services

    return sorted_services


class ServiceInteraction:
    def __init__(
        self,
        name: str = None,
        outputs: t.List[str] = None,
        execute: bool = None,
        install_packages: bool = None,
        missing_modules: t.List[str] = None,
        quiet: bool = None,
        # still_missing_modules: t.List[str] = None,
        # unresolved_modules: t.List[str] = None,
    ):
        self.name = name
        self.outputs = outputs
        self.install_packages = install_packages
        self.missing_modules = missing_modules
        self.execute = execute
        self.quiet = quiet
        # self.still_missing_modules = still_missing_modules
        # self.unresolved_modules = unresolved_modules

    def to_dict(self):
        ret = {
            ret: val
            for ret, val in deepcopy(self.__dict__).items()
            if val is not None and val != []
        }
        if self.install_packages == DEFAULT_AUTO_INSTALL_PACKAGES:
            del ret["install_packages"]
        if self.quiet == DEFAULT_QUIET:
            del ret["quiet"]

        return ret

    def get_code(self):
        if self.execute:
            return self.outputs[0]
        else:
            return ""
