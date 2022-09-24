import requests
import json
import copy
import shlex

import typing as t

from ..config import *
from .api_base import APIBase

ICORTEX_ENDPOINT_URI = "https://api.textcortex.com/hemingwai/generate_text_v2"
DEFAULT_N_GEN = 1
DEFAULT_TEMPERATURE = 0.1
DEFAULT_TOKEN_COUNT = 256
DEFAULT_SOURCE_LANGUAGE = "en"
MISSING_API_KEY_MSG = """The ICortex prompt requires an API key from TextCortex in order to work.

1.  Visit https://app.textcortex.com/user/dashboard/settings/api-key to view your API key.
    If you do not have an account, you can sign up at https://app.textcortex.com/user/signup.

2.  Create a file icortex.toml in in the same directory as your Jupyter Notebook with
    the following lines:

api = "textcortex"
[textcortex]
api_key = "your-api-key-goes-here"
"""


class TextCortexAPI(APIBase):
    name = "textcortex"

    def __init__(self, config: t.Dict):
        super(TextCortexAPI, self).__init__()

        try:
            self.api_key = config["api_key"]
        except KeyError:
            print(MISSING_API_KEY_MSG)
            raise Exception("Missing API key")

        # Add TextCortex specific arguments
        self.prompt_parser.description = "TextCortex Python code generator."
        self.prompt_parser.add_argument(
            "-t",
            "--temperature",
            type=float,
            default=DEFAULT_TEMPERATURE,
            required=False,
            help=f"Temperature controls the amount of randomness in the generated output. Must be between 0 and 1. Default: {DEFAULT_TEMPERATURE}",
        )
        self.prompt_parser.add_argument(
            "-n",
            "--n-gen",
            type=int,
            default=1,
            required=False,
            help=f"Number of outputs to be generated. Default: {DEFAULT_N_GEN}",
        )
        self.prompt_parser.add_argument(
            "-c",
            "--token-count",
            type=int,
            default=DEFAULT_TOKEN_COUNT,
            required=False,
            help=f"Maximum token count that the API should attempt to generate. Default: {DEFAULT_TOKEN_COUNT}",
        )
        self.prompt_parser.add_argument(
            "-l",
            "--language",
            type=str,
            default=DEFAULT_SOURCE_LANGUAGE,
            help=f"ISO 639-1 code of the language that the prompt is in. Default: {DEFAULT_SOURCE_LANGUAGE}",
            required=False,
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
            "template_name": "code_cortex_python",
            "prompt": {"instruction": prompt},
            "temperature": args.temperature,
            "word_count": args.token_count,
            "n_gen": args.n_gen,
            "source_language": args.language,
            "api_key": self.api_key,
        }
        headers = {"Content-Type": "application/json"}

        # Create a dict of the request for cache storage
        cached_payload = copy.deepcopy(payload)
        del cached_payload["api_key"]
        cached_request_dict = {
            "api": "textcortex",
            "params": {
                "type": "POST",
                "path": ICORTEX_ENDPOINT_URI,
                "headers": headers,
                "data": cached_payload,
            },
        }

        # If the the same request is found in the cache, return the cached response
        if not args.regenerate:
            cached_response = self.find_cached_response(
                cached_request_dict, cache_path=DEFAULT_CACHE_PATH
            )
            if cached_response is not None:
                return cached_response["generated_text"]

        # Otherwise, make the API call
        response = requests.request(
            "POST", ICORTEX_ENDPOINT_URI, headers=headers, data=json.dumps(payload)
        )

        response_dict = response.json()
        if response_dict["status"] == "success":
            self.cache_response(
                cached_request_dict, response_dict, cache_path=DEFAULT_CACHE_PATH
            )

            return response_dict["generated_text"]
        elif response_dict["status"] == "fail":
            raise Exception(
                f"There was an issue with generation: {response_dict['message']}"
            )
