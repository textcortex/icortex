import shlex

import typing as t


from icortex.config import *
from icortex.helper import unescape
from icortex.services import ServiceBase, ServiceOption


DEFAULT_MODEL = "facebook/incoder-1B"


def create_prompt(input: str, prefix: str, suffix: str):
    return prefix + input + suffix


class HuggingFaceAutoService(ServiceBase):
    name = "hfauto"
    description = "TextCortex Python code generator"
    options = {
        "model": ServiceOption(
            str,
            help="Model name or path",
            default=DEFAULT_MODEL,
        ),
        "temperature": ServiceOption(
            float,
            default=0.2,
            help=f"Temperature controls the amount of randomness in the generated output. Must be between 0 and 1.",
            argparse_args=["-t", "--temperature"],
        ),
        "n_gen": ServiceOption(
            int,
            default=1,
            help=f"Number of outputs to be generated.",
            argparse_args=["-n", "--n-gen"],
        ),
        "max_length": ServiceOption(
            int,
            default=256,
            help=f"Maximum token count that the API should attempt to generate.",
            argparse_args=["-c", "--max_length"],
        ),
        "prompt_prefix": ServiceOption(
            str,
            default=r"# ",
            help=f"String to prepend to your prompt.",
            argparse_args=["--prompt-prefix"],
        ),
        "prompt_suffix": ServiceOption(
            str,
            default=r"\n```python3\n",
            help=f"String to append to your prompt.",
            argparse_args=["--prompt-suffix"],
        ),
        "stop": ServiceOption(
            str,
            default="```",
            help=f"Up to 4 sequences where the API will stop generating further tokens. The returned text will not contain the stop sequence.",
            argparse_args=["--stop"],
        ),
    }

    def __init__(self, config: t.Dict):
        super(HuggingFaceAutoService, self).__init__(config)

        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM

        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        if "model" in config:
            model_name_or_path = config["model"]
        else:
            model_name_or_path = DEFAULT_MODEL

        self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)

        self.model = (
            AutoModelForCausalLM.from_pretrained(model_name_or_path)
            .eval()
            .to(self.device)
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

        prompt_text = create_prompt(
            " ".join(args.prompt),
            unescape(args.prompt_prefix),
            unescape(args.prompt_suffix),
        )

        # Prepare request data
        payload = {
            "prompt": prompt_text,
            "temperature": args.temperature,
            "max_length": args.max_length,
            # "n_gen": args.n_gen,
        }

        # Create a dict of the request for cache storage
        cached_request_dict = {
            "service": self.name,
            "data": payload,
        }

        # If the the same request is found in the cache, return the cached response
        if not args.regenerate:
            cached_response = self.find_cached_response(
                cached_request_dict, cache_path=DEFAULT_CACHE_PATH
            )
            if cached_response is not None:
                return cached_response["generated_text"]

        # Inference
        code = self._generate(**payload)
        response_dict = {"generated_text": [{"text": code}]}

        self.cache_response(
            cached_request_dict, response_dict, cache_path=DEFAULT_CACHE_PATH
        )

        return response_dict["generated_text"]

    def _generate(
        self,
        prompt=None,
        max_length=64,
        temperature=0.2,
        num_return_sequences=1,
    ):
        input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids.to(
            self.device
        )
        generated_ids = self.model.generate(
            input_ids,
            max_length=max_length,
            temperature=temperature,
            num_return_sequences=num_return_sequences,
            early_stopping=True,
        )
        return self.tokenizer.decode(generated_ids[0], skip_special_tokens=True)


# TODO
# [x] Keep the ServiceBase object in memory and don't create a new one every time
# [ ] Model config is pulled during config dialog
