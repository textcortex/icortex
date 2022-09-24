import os
import argparse
import json

from ..config import *

import typing as t


class APIBase:
    name = "base"

    def __init__(self):
        # Create the prompt parser and add default arguments
        # Each child class will need to add their specific arguments
        # by extending self.prompt_parser.
        self.prompt_parser = argparse.ArgumentParser(
            add_help=False,
        )
        self.prompt_parser.add_argument(
            "prompt",
            nargs="*",
            type=str,
            help="The prompt that describes what the generated Python code should perform.",
        )
        self.prompt_parser.add_argument(
            "-e",
            "--execute",
            action="store_true",
            required=False,
            help="Execute the Python code returned by the TextCortex API in the same cell.",
        )
        self.prompt_parser.add_argument(
            "-r",
            "--regenerate",
            action="store_true",
            required=False,
            help="Make the kernel ignore cached responses and makes a new request to the TextCortex API.",
        )
        self.prompt_parser.add_argument(
            "-i",
            "--include-history",
            action="store_true",
            required=False,
            help="Submit notebook history along with the prompt.",
        )
        self.prompt_parser.add_argument(
            "-p",
            "--auto-install-packages",
            action="store_true",
            required=False,
            help="Auto-install packages that are imported in the generated code but missing in the active Python environment.",
        )
        self.prompt_parser.add_argument(
            "-o",
            "--nonint",
            action="store_true",
            required=False,
            help=f"Non-interactive, do not ask any questions.",
        )
        self.prompt_parser.add_argument(
            "-h",
            "--hide-code",
            action="store_true",
            required=False,
            help="Do not print the generated code.",
        )
        self.prompt_parser.usage = "/your prompt goes here [-e] [-r] [-i] [-p] ..."

    def find_cached_response(
        self,
        request_dict: t.Dict,
        cache_path: str = DEFAULT_CACHE_PATH,
    ):
        cache = self._read_cache(cache_path)
        # If the the same request is found in the cache, return the cached response
        # Return the latest found response by default
        for dict_ in reversed(cache):
            if dict_["request"] == request_dict:
                return dict_["response"]
        return None

    def cache_response(
        self,
        request_dict: t.Dict,
        response_dict: t.Dict,
        cache_path: str = DEFAULT_CACHE_PATH,
    ):
        cache = self._read_cache(DEFAULT_CACHE_PATH)
        cache.append({"request": request_dict, "response": response_dict})
        return self._write_cache(cache, cache_path)

    def generate(self, prompt: str):
        raise NotImplementedError

    def _read_cache(self, cache_path):
        # Check whether the cache file already exists
        if os.path.exists(cache_path):
            try:
                with open(cache_path, "r") as f:
                    cache = json.load(f)
            except json.decoder.JSONDecodeError:
                cache = []
        else:
            cache = []
        return cache

    def _write_cache(self, cache: t.List[t.Dict], cache_path):
        with open(cache_path, "w") as f:
            json.dump(cache, f, indent=2)
        return True
