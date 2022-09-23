from .textcortex import TextCortexAPI
# from .openai import OpenAIApi

api_dict = {
    "textcortex": TextCortexAPI
}

def get_api(name: str):
    return api_dict[name]