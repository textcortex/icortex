import openai
import shlex

import typing as t

from icortex.defaults import *
from icortex.services import ServiceBase, ServiceVariable
from icortex.helper import unescape

MISSING_API_KEY_MSG = """The ICortex prompt requires an API key from OpenAI in order to work.

1.  Generate an API key in the OpenAI web interface, https://beta.openai.com/account/api-keys.

2.  Create a file icortex.toml in in the same directory as your Jupyter Notebook with
    the following lines:

service = "openai"
[openai]
api_key = "your-api-key-goes-here"
"""


def create_prompt(input: str, prefix: str, suffix: str):
    return prefix + input + suffix


class OpenAIService(ServiceBase):
    name = "openai"
    description = "OpenAI Python code generator that uses the Codex API."
    variables = {
        "api_key": ServiceVariable(
            str,
            help="If you don't have an API key already, generate one in the OpenAI web interface, https://beta.openai.com/account/api-keys",
            secret=True,
        ),
        "model": ServiceVariable(
            str,
            default="code-davinci-002",
            help=f"Model to use.",
            argparse_args=["--model"],  # "-m", TODO: Resolve the module name flag issue
        ),
        "temperature": ServiceVariable(
            float,
            default=0.1,
            help=f"What sampling temperature to use. Higher values means the model will take more risks. Try 0.9 for more creative applications, and 0 (argmax sampling) for ones with a well-defined answer.",
            argparse_args=["-t", "--temperature"],
        ),
        "max_tokens": ServiceVariable(
            int,
            default=256,
            help=f"The maximum number of tokens to generate in the completion.",
            argparse_args=["-c", "--max-tokens"],
        ),
        "top_p": ServiceVariable(
            float,
            default=1.0,
            argparse_args=["--top-p"],
            help=f"An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10 percent probability mass are considered.",
        ),
        "n": ServiceVariable(
            int,
            default=1,
            help=f"Number of outputs to be generated.",
            argparse_args=["-n", "--n-gen"],
        ),
        "frequency_penalty": ServiceVariable(
            float,
            default=0.0,
            help=f"Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim.",
            argparse_args=["--frequency-penalty"],
        ),
        "presence_penalty": ServiceVariable(
            float,
            default=0.0,
            help=f"Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics.",
            argparse_args=["--presence-penalty"],
        ),
        "prompt_prefix": ServiceVariable(
            str,
            default=r"# ",
            help=f"String to prepend to your prompt.",
            argparse_args=["--prompt-prefix"],
        ),
        "prompt_suffix": ServiceVariable(
            str,
            default=r"\n```python3\n",
            help=f"String to append to your prompt.",
            argparse_args=["--prompt-suffix"],
        ),
        "stop": ServiceVariable(
            str,
            default="```",
            help=f"A sequence where the API will stop generating further tokens. The returned text will not contain the stop sequence.",
            argparse_args=["--stop"],
        ),
    }

    def __init__(self, config: t.Dict):
        super(OpenAIService, self).__init__(config)

        try:
            self.api_key = config["api_key"]
            openai.api_key = self.api_key
        except KeyError:
            print(MISSING_API_KEY_MSG)
            raise Exception("Missing OpenAI API key")

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
        openai_prompt = create_prompt(
            " ".join(args.prompt),
            unescape(args.prompt_prefix),
            unescape(args.prompt_suffix),
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
            "stop": [args.stop],
        }

        cached_request_dict = {
            "service": self.name,
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
