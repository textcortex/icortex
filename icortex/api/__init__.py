from .textcortex import TextCortexAPI
from .openai import OpenAIAPI

api_dict = {
    "textcortex": TextCortexAPI,
    "openai": OpenAIAPI,
}


def get_api(name: str):
    return api_dict[name]
