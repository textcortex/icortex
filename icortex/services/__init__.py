from icortex.services.service_base import ServiceBase, ServiceOption
from icortex.services.textcortex import TextCortexService
from icortex.services.openai import OpenAIService

service_dict = {
    "textcortex": TextCortexService,
    "openai": OpenAIService,
}


def get_service(name: str):
    return service_dict[name]
