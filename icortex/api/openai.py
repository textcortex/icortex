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
    "stop": ["```"],
}
MISSING_API_KEY_MSG = """The ICortex prompt requires an API key from OpenAI in order to work.

TODO: Add instructions on fetching OpenAI key

api = "openai"
[openai]
api_key = "your-api-key-goes-here"
"""


def create_prompt(input):
    return f"""# {input}
```python3
"""


class TextCortexAPI(APIBase):
    def __init__(self, config: t.Dict):
        super(TextCortexAPI, self).__init__()

        try:
            self.textcortex_api_key = config["api_key"]
        except KeyError:
            print(MISSING_API_KEY_MSG)
            raise Exception("Missing OpenAI API key")

        # Add TextCortex specific arguments
        self.prompt_parser.description = "OpenAI Python code generator."
        self.prompt_parser.add_argument(
            "-m",
            "--model",
            type=float,
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
            help=f"Temperature controls the amount of randomness in the generated output. Must be between 0 and 1. Default: {DEFAULT_PARAMS['temperature']}",
        )
        self.prompt_parser.add_argument(
            "--top-p",
            type=float,
            default=DEFAULT_PARAMS["top-p"],
            required=False,
            help=f"TODO. Default: {DEFAULT_PARAMS['top-p']}",
        )
        self.prompt_parser.add_argument(
            "-n",
            "-n-gen",
            type=int,
            default=DEFAULT_PARAMS["n"],
            required=False,
            help=f"Number of outputs to be generated. Default: {DEFAULT_PARAMS['n']}",
        )
        self.prompt_parser.add_argument(
            "-c",
            "--max-tokens",
            type=int,
            default=DEFAULT_PARAMS["max-tokens"],
            required=False,
            help=f"Maximum token count that the API should attempt to generage. Default: {DEFAULT_PARAMS['max-tokens']}",
        )
        self.prompt_parser.add_argument(
            "--frequency-penalty",
            type=int,
            default=DEFAULT_PARAMS["frequency-penalty"],
            required=False,
            help=f"TODO. Default: {DEFAULT_PARAMS['frequency-penalty']}",
        )
        self.prompt_parser.add_argument(
            "--presence-penalty",
            type=int,
            default=DEFAULT_PARAMS["presence-penalty"],
            required=False,
            help=f"TODO. Default: {DEFAULT_PARAMS['presence-penalty']}",
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

        # Prepare request data
        payload = {
            "prompt": create_prompt(input),
            "model": args.model,
            "temperature": args.temperature,
            "max_tokens": args.max_tokens,
            "top_p": args.top_p,
            "n": args.n_gen,
            "frequency_penalty": args.frequency_penalty,
            "presence_penalty": args.presence_penalty,
        }

        # If the the same request is found in the cache, return the cached response
        if not args.regenerate:
            cached_response = self.find_cached_response(
                payload, cache_path=DEFAULT_CACHE_PATH
            )
            if cached_response is not None:
                return cached_response["generated_text"]

        # Otherwise, make the API call
        response = openai.Completion.create(**payload)

        if response["status"] == "success":
            self.cache_response(payload, response, cache_path=DEFAULT_CACHE_PATH)

            return response["choices"]
        elif response["status"] == "fail":
            raise Exception(
                f"There was an issue with generation: {response['message']}"
            )
