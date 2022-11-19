import typing as t
from icortex.context import ICortexContext
from icortex.defaults import *
from icortex.services import ServiceBase, ServiceVariable
from icortex.helper import escape_quotes
from icortex.services.generation_result import GenerationResult

class EchoService(ServiceBase):
    name = "echo"
    description = "Service used for testing"
    hidden = True
    variables = {
        "prefix": ServiceVariable(
            str,
            help="Prefix to add to the input before printing",
            default=">>> ",
            argparse_args=["--prefix"],
        ),
    }

    def generate(
        self,
        prompt: str,
        args,
        context: ICortexContext = None,
    ) -> GenerationResult:

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

        desired_output = args.prefix + " ".join(args.prompt)
        code = 'print("""' + escape_quotes(desired_output) + '""")'

        response_dict = {"generated_text": [{"text": code}]}

        self.cache_interaction(
            cached_request_dict, response_dict, cache_path=DEFAULT_CACHE_PATH
        )

        return GenerationResult(cached_request_dict, response_dict)

    def get_outputs_from_result(
        self, generation_result: GenerationResult
    ) -> t.List[str]:
        ret = [i["text"] for i in generation_result.response_dict["generated_text"]]
        return ret
