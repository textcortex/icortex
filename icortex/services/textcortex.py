import os
import requests
import json
import copy

import typing as t
from icortex.context import ICortexContext

from icortex.defaults import *
from icortex.services import ServiceBase, ServiceVariable
from icortex.services.generation_result import GenerationResult

ICORTEX_ENDPOINT_URI = "https://api.textcortex.com/hemingwai/generate_text_v3"
MISSING_API_KEY_MSG = """The ICortex prompt requires an API key from TextCortex in order to work.

1.  Visit https://app.textcortex.com/user/dashboard/settings/api-key to view your API key.
    If you do not have an account, you can sign up at https://app.textcortex.com/user/signup?registration_source=icortex .

2.  Create a file icortex.toml in in the same directory as your Jupyter Notebook with
    the following lines:

service = "textcortex"
[textcortex]
api_key = "your-api-key-goes-here"
"""

# Load alternative URI from the environment
try:
    from dotenv import load_dotenv

    load_dotenv()
    ICORTEX_ENDPOINT_URI = os.environ.get("ICORTEX_ENDPOINT_URI", ICORTEX_ENDPOINT_URI)
except:
    pass


class TextCortexService(ServiceBase):
    """Interface to TextCortex's code generation service"""

    name = "textcortex"
    description = "TextCortex Python code generator"
    variables = {
        "api_key": ServiceVariable(
            str,
            help="If you don't have a TextCortex account, create one here (no payment information required): https://app.textcortex.com/user/signup?registration_source=icortex . If you already have an account, get your API key at https://app.textcortex.com/user/dashboard/settings/api-key ",  # Leave a space at the end
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

    def __init__(self, **kwargs: t.Dict):
        super(TextCortexService, self).__init__(**kwargs)

        try:
            self.api_key = kwargs["api_key"]
        except KeyError:
            print(MISSING_API_KEY_MSG)
            raise Exception("Missing API key")

    def generate(
        self,
        prompt: str,
        args,
        context: ICortexContext = None,
    ) -> t.List[t.Dict[t.Any, t.Any]]:
        """"""

        # Prepare request data
        payload = {
            "template_name": "icortex",
            "prompt": {
                "instruction": prompt,
                "context": context.to_dict() if context else {},
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
            cached_interaction = self.find_cached_interaction(
                cached_request_dict, cache_path=DEFAULT_CACHE_PATH
            )
            if cached_interaction is not None:
                if cached_interaction.execute == True:
                    return cached_interaction.generation_result

        # Otherwise, make the API call
        response = requests.request(
            "POST", ICORTEX_ENDPOINT_URI, headers=headers, data=json.dumps(payload)
        )

        response_dict = response.json()
        if response_dict.get("status") == "success":
            return GenerationResult(cached_request_dict, response_dict)
            # return response_dict["generated_text"]
        else:
            raise Exception(
                f"There was an issue with generation: {response_dict.get('message', 'No message provided')}"
            )

    def get_outputs_from_result(
        self, generation_result: GenerationResult
    ) -> t.List[str]:
        ret = [i["text"] for i in generation_result.response_dict["generated_text"]]
        return ret
