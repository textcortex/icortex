from icortex.service.service_base import ServiceBase, ServiceOption
from icortex.service.textcortex import TextCortexService
from icortex.service.openai import OpenAIService

service_dict = {
    "textcortex": TextCortexService,
    "openai": OpenAIService,
}


def get_service(name: str):
    return service_dict[name]
