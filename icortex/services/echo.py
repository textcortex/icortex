import shlex

from icortex.config import *
from icortex.services import ServiceBase, ServiceOption
from icortex.helper import unescape


class EchoService(ServiceBase):
    name = "echo"
    description = "Service used for testing"
    hidden = True
    options = {
        "prefix": ServiceOption(
            str,
            help="Prefix to add to the input before printing",
            default=">>> ",
            argparse_args=["--prefix"],
        ),
    }

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
            "prompt": args.prompt,
            "prefix": args.prefix,
        }

        # Create a dict of the request for cache storage
        cached_request_dict = {
            "service": "echo",
            "data": payload,
        }

        # If the the same request is found in the cache, return the cached response
        if not args.regenerate:
            cached_response = self.find_cached_response(
                cached_request_dict, cache_path=DEFAULT_CACHE_PATH
            )
            if cached_response is not None:
                return cached_response["generated_text"]

        desired_output = args.prefix + " ".join(args.prompt)
        code = 'print("""' + desired_output.replace('"""', r"\"\"\"") + '""")'

        response_dict = {"generated_text": [{"text": code}]}

        self.cache_response(
            cached_request_dict, response_dict, cache_path=DEFAULT_CACHE_PATH
        )

        return response_dict["generated_text"]