import requests
import json
import copy
import shlex

import typing as t

from icortex.defaults import *
from icortex.services import ServiceBase, ServiceVariable

ICORTEX_ENDPOINT_URI = "https://api.textcortex.com/hemingwai/generate_text_v3"
MISSING_API_KEY_MSG = """The ICortex prompt requires an API key from TextCortex in order to work.

1.  Visit https://app.textcortex.com/user/dashboard/settings/api-key to view your API key.
    If you do not have an account, you can sign up at https://app.textcortex.com/user/signup.

2.  Create a file icortex.toml in in the same directory as your Jupyter Notebook with
    the following lines:

service = "textcortex"
[textcortex]
api_key = "your-api-key-goes-here"
"""


class TextCortexService(ServiceBase):
    name = "textcortex"
    description = "TextCortex Python code generator"
    variables = {
        "api_key": ServiceVariable(
            str,
            help="If you don't have an API key already, generate one at https://app.textcortex.com/user/dashboard/settings/api-key ",  # Leave a space at the end
            secret=True,
        ),
        "temperature": ServiceVariable(
            float,
            default=0.1,
            help=f"Temperature controls the amount of randomness in the generated output. Must be between 0 and 1.",
            argparse_args=["-t", "--temperature"],
        ),
        "n_gen": ServiceVariable(
            int,
            default=1,
            help=f"Number of outputs to be generated.",
            argparse_args=["-n", "--n-gen"],
        ),
        "token_count": ServiceVariable(
            int,
            default=256,
            help=f"Maximum token count that the API should attempt to generate.",
            argparse_args=["-c", "--token-count"],
        ),
        "language": ServiceVariable(
            str,
            default="en",
            help=f"ISO 639-1 code of the language that the prompt is in.",
            argparse_args=["-l", "--language"],
        ),
    }

    def __init__(self, config: t.Dict):
        super(TextCortexService, self).__init__(config)

        try:
            self.api_key = config["api_key"]
        except KeyError:
            print(MISSING_API_KEY_MSG)
            raise Exception("Missing API key")

    def generate(
        self,
        prompt: str,
        context: t.Dict[str, t.Any] = {},
    ):
        argv = shlex.split(prompt)

        # Remove the module name flag from the prompt
        # Argparse adds this automatically, so we need to sanitize user input
        if "-m" in argv:
            argv.remove("-m")

        args = self.prompt_parser.parse_args(argv)
        prompt_text = " ".join(args.prompt)
        # Prepare request data
        payload = {
            "template_name": "icortex",
            "prompt": {
                "instruction": prompt_text,
                "context": context,
            },
            "temperature": args.temperature,
            "token_count": args.token_count,
            "n_gen": args.n_gen,
            "source_language": args.language,
            "api_key": self.api_key,
        }
        headers = {"Content-Type": "application/json"}

        # Create a dict of the request for cache storage
        cached_payload = copy.deepcopy(payload)
        del cached_payload["api_key"]
        # Delete the whole context for now:
        del cached_payload["prompt"]["context"]
        cached_request_dict = {
            "service": self.name,
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
