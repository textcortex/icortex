import openai
import copy
import shlex

import typing as t

from ..config import *
from .api_base import APIBase

DEFAULT_PARAMS = {
    "model": "code-davinci-002",
    "temperature": 0.1,
    "max_tokens": 256,
    "top_p": 1,
    "n": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0,
    "prompt_prefix": r"# ",
    "prompt_suffix": r"\n```python3\n",
    "stop": ["```"],
}
MISSING_API_KEY_MSG = """The ICortex prompt requires an API key from OpenAI in order to work.

1.  Generate an API key in the OpenAI web interface, https://beta.openai.com/account/api-keys.

2.  Create a file icortex.toml in in the same directory as your Jupyter Notebook with
    the following lines:

api = "openai"
[openai]
api_key = "your-api-key-goes-here"
"""


def create_prompt(input: str, prefix: str, suffix: str):
    return prefix + input + suffix


def unescape(s):
    return s.encode("utf-8").decode("unicode_escape")


class OpenAIAPI(APIBase):
    name = "openai"

    def __init__(self, config: t.Dict):
        super(OpenAIAPI, self).__init__()

        try:
            self.api_key = config["api_key"]
            openai.api_key = self.api_key
        except KeyError:
            print(MISSING_API_KEY_MSG)
            raise Exception("Missing OpenAI API key")

        # Add TextCortex specific arguments
        self.prompt_parser.description = "OpenAI Python code generator."
        self.prompt_parser.add_argument(
            # "-m", # TODO: Resolve the module name flag issue
            "--model",
            type=str,
            default=DEFAULT_PARAMS["model"],
            required=False,
            help=f"Model to use. Default: {DEFAULT_PARAMS['model']}",
        )
        self.prompt_parser.add_argument(
            "-t",
            "--temperature",
            type=float,
            default=DEFAULT_PARAMS["temperature"],
            required=False,
            help=f"What sampling temperature to use. Higher values means the model will take more risks. Try 0.9 for more creative applications, and 0 (argmax sampling) for ones with a well-defined answer. Default: {DEFAULT_PARAMS['temperature']}",
        )
        self.prompt_parser.add_argument(
            "--top-p",
            type=float,
            default=DEFAULT_PARAMS["top_p"],
            required=False,
            help=f"An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10 percent probability mass are considered. Default: {DEFAULT_PARAMS['top_p']}",
        )
        self.prompt_parser.add_argument(
            "-n",
            "--n-gen",
            type=int,
            default=DEFAULT_PARAMS["n"],
            required=False,
            help=f"Number of outputs to be generated. Default: {DEFAULT_PARAMS['n']}",
        )
        self.prompt_parser.add_argument(
            "-c",
            "--max-tokens",
            type=int,
            default=DEFAULT_PARAMS["max_tokens"],
            required=False,
            help=f"The maximum number of tokens to generate in the completion. Default: {DEFAULT_PARAMS['max_tokens']}",
        )
        self.prompt_parser.add_argument(
            "--frequency-penalty",
            type=int,
            default=DEFAULT_PARAMS["frequency_penalty"],
            required=False,
            help=f"Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim. Default: {DEFAULT_PARAMS['frequency_penalty']}",
        )
        self.prompt_parser.add_argument(
            "--presence-penalty",
            type=int,
            default=DEFAULT_PARAMS["presence_penalty"],
            required=False,
            help=f"Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics. Default: {DEFAULT_PARAMS['presence_penalty']}",
        )
        self.prompt_parser.add_argument(
            "--prompt-prefix",
            type=str,
            default=DEFAULT_PARAMS["prompt_prefix"],
            required=False,
            help=f"String to prepend to your prompt. Default: {repr(DEFAULT_PARAMS['prompt_prefix'])}",
        )
        self.prompt_parser.add_argument(
            "--prompt-suffix",
            type=str,
            default=DEFAULT_PARAMS["prompt_suffix"],
            required=False,
            help=f"String to append to your prompt. Default: {repr(DEFAULT_PARAMS['prompt_suffix'])}",
        )
        self.prompt_parser.add_argument(
            "--stop",
            type=str,
            default=DEFAULT_PARAMS["stop"],
            required=False,
            help=f"Up to 4 sequences where the API will stop generating further tokens. The returned text will not contain the stop sequence. Default: {DEFAULT_PARAMS['stop']}",
        )

    def generate(
        self,
        prompt: str,
    ):

        argv = shlex.split(prompt)

        # Remove the module name flag from the prompt
        # Argparse adds this automatically, so we need to sanitize user input
        if "-m" in argv:
            argv.remove("-m")

        args = self.prompt_parser.parse_args(argv)
        openai_prompt = create_prompt(
            " ".join(args.prompt), unescape(args.prompt_prefix), unescape(args.prompt_suffix)
        )

        # Prepare request data
        request_dict = {
            "prompt": openai_prompt,
            "model": args.model,
            "temperature": args.temperature,
            "max_tokens": args.max_tokens,
            "top_p": args.top_p,
            "n": args.n_gen,
            "frequency_penalty": args.frequency_penalty,
            "presence_penalty": args.presence_penalty,
            "stop": args.stop,
        }

        cached_request_dict = {
            "api": "openai",
            "params": request_dict,
        }

        # If the the same request is found in the cache, return the cached response
        if not args.regenerate:
            cached_response = self.find_cached_response(
                cached_request_dict, cache_path=DEFAULT_CACHE_PATH
            )
            if cached_response is not None:
                return cached_response["choices"]

        # Otherwise, make the API call
        response = openai.Completion.create(**request_dict)

        self.cache_response(
            cached_request_dict, response, cache_path=DEFAULT_CACHE_PATH
        )

        return response["choices"]
