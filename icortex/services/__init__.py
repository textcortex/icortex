from icortex.services.service_base import ServiceBase, ServiceOption
from icortex.services.echo import EchoService
from icortex.services.textcortex import TextCortexService
from icortex.services.openai import OpenAIService
from icortex.services.huggingface import HuggingFaceAutoService

service_dict = {
    "echo": EchoService,
    "textcortex": TextCortexService,
    "openai": OpenAIService,
    "hfauto": HuggingFaceAutoService,
}


def get_service(name: str):
    return service_dict[name]
