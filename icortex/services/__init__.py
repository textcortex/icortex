import typing as t
from copy import deepcopy

from icortex.services.service_base import ServiceBase, ServiceVariable
from icortex.services.echo import EchoService
from icortex.services.textcortex import TextCortexService
from icortex.services.openai import OpenAIService
from icortex.services.huggingface import HuggingFaceAutoService

from icortex.defaults import (
    DEFAULT_AUTO_EXECUTE,
    DEFAULT_AUTO_INSTALL_PACKAGES,
    DEFAULT_QUIET,
    DEFAULT_SERVICE,
)

service_dict = {
    "echo": EchoService,
    "textcortex": TextCortexService,
    "openai": OpenAIService,
    "huggingface": HuggingFaceAutoService,
}


def get_service(name: str) -> t.Type[ServiceBase]:
    return service_dict[name]


def get_available_services() -> t.List[str]:
    sorted_services = sorted(
        [key for key, val in service_dict.items() if not val.hidden]
    )
    sorted_services.remove(DEFAULT_SERVICE)
    sorted_services = [DEFAULT_SERVICE] + sorted_services

    return sorted_services


class ServiceInteraction:
    def __init__(
        self,
        name: str = None,
        outputs: t.List[str] = None,
        auto_execute: bool = None,
        execute_yesno: bool = None,
        did_execute: bool = None,
        quiet: bool = None,
        auto_install_packages: bool = None,
        missing_modules: t.List[str] = None,
        still_missing_modules: t.List[str] = None,
        unresolved_modules: t.List[str] = None,
    ):
        self.name = name
        self.outputs = outputs
        self.auto_install_packages = auto_install_packages
        self.missing_modules = missing_modules
        self.still_missing_modules = still_missing_modules
        self.auto_execute = auto_execute
        self.execute_yesno = execute_yesno
        self.did_execute = did_execute
        self.quiet = quiet
        self.unresolved_modules = unresolved_modules

    def to_dict(self):
        ret = {
            ret: val
            for ret, val in deepcopy(self.__dict__).items()
            if val is not None and val != []
        }
        if self.auto_install_packages == DEFAULT_AUTO_INSTALL_PACKAGES:
            del ret["auto_install_packages"]
        if self.auto_execute == DEFAULT_AUTO_EXECUTE:
            del ret["auto_execute"]
        if self.quiet == DEFAULT_QUIET:
            del ret["quiet"]

        return ret

    def get_code(self):
        if self.did_execute:
            return self.outputs[0]
        else:
            return ""
