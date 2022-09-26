from icortex.services.service_base import ServiceBase, ServiceOption
from icortex.services.textcortex import TextCortexService
from icortex.services.openai import OpenAIService
from icortex.services.echo import EchoService

service_dict = {
    "textcortex": TextCortexService,
    "openai": OpenAIService,
    "echo": EchoService,
}


def get_service(name: str):
    return service_dict[name]
