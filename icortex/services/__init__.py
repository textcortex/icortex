from icortex.services.service_base import ServiceBase, ServiceOption
from icortex.services.echo import EchoService
from icortex.services.textcortex import TextCortexService
from icortex.services.openai import OpenAIService
from icortex.services.huggingface import HuggingFaceAutoService
from icortex.config import DEFAULT_SERVICE
import typing as t

service_dict = {
    "echo": EchoService,
    "textcortex": TextCortexService,
    "openai": OpenAIService,
    "huggingface": HuggingFaceAutoService,
}


def get_service(name: str):
    return service_dict[name]


def get_available_services() -> t.List[str]:
    sorted_services = sorted(
        [key for key, val in service_dict.items() if not val.hidden]
    )
    sorted_services.remove(DEFAULT_SERVICE)
    sorted_services = [DEFAULT_SERVICE] + sorted_services

    return sorted_services
