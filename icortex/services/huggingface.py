import re
import typing as t

from icortex.defaults import *
from icortex.helper import unescape
from icortex.services import ServiceBase, ServiceVariable
from icortex.context import ICortexContext
from icortex.services.generation_result import GenerationResult

# TODO
# [x] Keep the ServiceBase object in memory and don't create a new one at every request
# [ ] Model config is pulled during config dialog

DEFAULT_MODEL = "TextCortex/codegen-350M-optimized"


def build_prompt(input: str, prefix: str, suffix: str):
    return prefix + input + suffix


# Map from initializer classes to pretrained model filenames
PRETRAINED_FILENAMES = {
    "AutoModelForCausalLM": [
        "pytorch_model.bin",
        "tf_model.h5",
        "model.ckpt",
        "flax_model.msgpack",
        r"model*.pt",
    ],
    "ORTModelForCausalLM": [
        r"model*.onnx",
    ],
}


def get_model_initializer(model_id):
    from huggingface_hub.hf_api import list_repo_files

    files = list_repo_files(model_id)

    for initializer, candidates in PRETRAINED_FILENAMES.items():
        for candidate in candidates:
            for file in files:
                if re.match(candidate, file) is not None:
                    return initializer
    return None


class HuggingFaceAutoService(ServiceBase):
    name = "huggingface"
    description = "Service to generate code using HuggingFace models"
    variables = {
        "model": ServiceVariable(
            str,
            help="Model id",
            default=DEFAULT_MODEL,
        ),
        "temperature": ServiceVariable(
            float,
            default=0.2,
            help=f"Temperature controls the amount of randomness in the generated output. Must be between 0 and 1.",
            argparse_args=["-t", "--temperature"],
        ),
        "n_gen": ServiceVariable(
            int,
            default=1,
            help=f"Number of outputs to be generated.",
            argparse_args=["-n", "--n-gen"],
        ),
        "max_length": ServiceVariable(
            int,
            default=256,
            help=f"Maximum token count that the API should attempt to generate.",
            argparse_args=["-c", "--max_length"],
        ),
        "prompt_prefix": ServiceVariable(
            str,
            default=r"",
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

    def __init__(self, **kwargs: t.Dict):
        super(HuggingFaceAutoService, self).__init__(**kwargs)

        import torch
        from transformers import AutoTokenizer

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.token_id_cache = {}

        if "model" in kwargs:
            model_id = kwargs["model"]
        else:
            model_id = DEFAULT_MODEL

        initializer = get_model_initializer(model_id)

        # Tokenizer is always initialized with AutoTokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)

        # For the model itself, we need to use the respective auto initializers
        # print("Loading HuggingFace model ", model_id)

        if initializer == "AutoModelForCausalLM":
            from transformers import AutoModelForCausalLM

            self.model = AutoModelForCausalLM.from_pretrained(model_id)

            if hasattr(self.model, "eval"):
                self.model = self.model.eval().to(self.device)
        elif initializer == "ORTModelForCausalLM":
            from optimum.onnxruntime import ORTModelForCausalLM

            self.model = ORTModelForCausalLM.from_pretrained(model_id)
        else:
            raise Exception(
                f"Could not find an appropriate initializer for model {model_id}"
            )

    def generate(
        self,
        prompt: str,
        args,
        context: ICortexContext = None,
    ) -> GenerationResult:

        prompt_text = build_prompt(
            prompt,
            unescape(args.prompt_prefix),
            unescape(args.prompt_suffix),
        )

        # Prepare request data
        payload = {
            "prompt": prompt_text,
            "stop": args.stop,
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
            cached_interaction = self.find_cached_interaction(
                cached_request_dict, cache_path=DEFAULT_CACHE_PATH
            )
            if cached_interaction is not None:
                if cached_interaction.execute == True:
                    return cached_interaction.generation_result

        # Inference
        code = self._generate(**payload)
        response_dict = {"generated_text": [{"text": code}]}

        return GenerationResult(cached_request_dict, response_dict)

    def _generate(
        self,
        prompt=None,
        stop="```",
        max_length=64,
        temperature=0.2,
        num_return_sequences=1,
    ):
        # Tokenize input
        input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids.to(
            self.device
        )
        # Generate
        generated_ids = self.model.generate(
            input_ids,
            max_length=max_length,
            temperature=temperature,
            num_return_sequences=num_return_sequences,
            early_stopping=True,
            eos_token_id=self.get_token_id(stop),
        )
        output = self.tokenizer.decode(generated_ids[0], skip_special_tokens=True)

        # Postprocess
        output = output[: -len(stop)]
        output = output[len(prompt) :]
        output = output.rstrip()

        return output

    def get_token_id(self, seq):
        if seq in self.token_id_cache:
            return self.token_id_cache[seq]

        result = self.tokenizer(seq)
        ids = result["input_ids"][1:]
        assert len(ids) == 1
        token_id = ids[0]
        self.token_id_cache[seq] = token_id

        return token_id

    def get_outputs_from_result(
        self, generation_result: GenerationResult
    ) -> t.List[str]:
        ret = [i["text"] for i in generation_result.response_dict["generated_text"]]
        return ret
