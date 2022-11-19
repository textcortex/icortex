import typing as t
from copy import deepcopy

from icortex.defaults import (
    DEFAULT_AUTO_INSTALL_PACKAGES,
    DEFAULT_QUIET,
)


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

    def from_dict(d: dict):
        return ServiceInteraction(**d)

    def get_code(self) -> str:
        if self.execute:
            # TODO: Account for multiple generations
            return self.outputs[0]
        else:
            return ""
