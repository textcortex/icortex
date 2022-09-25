from .textcortex import TextCortexService
from .openai import OpenAIService

service_dict = {
    "textcortex": TextCortexService,
    "openai": OpenAIService,
}


def get_service(name: str):
    return service_dict[name]
