import typing as t
from copy import deepcopy

from icortex.defaults import (
    DEFAULT_AUTO_INSTALL_PACKAGES,
    DEFAULT_QUIET,
)
from icortex.services.generation_result import GenerationResult


class ServiceInteraction:
    def __init__(
        self,
        name: str = None,
        args: t.List[str] = None,
        generation_result: GenerationResult = None,
        outputs: t.List[str] = None,
        execute: bool = None,
        install_packages: bool = None,
        missing_modules: t.List[str] = None,
    ):
        self.name = name
        self.args = args
        self.generation_result = generation_result
        self.outputs = outputs
        self.install_packages = install_packages
        self.missing_modules = missing_modules
        self.execute = execute

    def to_dict(self):
        ret = {
            ret: val
            for ret, val in deepcopy(self.__dict__).items()
            if val is not None and val != []
        }
        if self.install_packages == DEFAULT_AUTO_INSTALL_PACKAGES:
            del ret["install_packages"]
        ret["generation_result"] = self.generation_result.to_dict()
        return ret

    def from_dict(d: dict):
        return ServiceInteraction(
            name=d.get("name"),
            args=d.get("args"),
            generation_result=GenerationResult.from_dict(d.get("generation_result")),
            outputs=d.get("outputs"),
            install_packages=d.get("install_packages"),
            missing_modules=d.get("missing_modules"),
            execute=d.get("execute"),
        )

    def get_code(self) -> str:
        if self.execute:
            # TODO: Account for multiple generations
            return self.outputs[0]
        else:
            return ""
