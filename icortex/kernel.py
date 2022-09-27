# Guides to writing Jupyter kernels:
# https://jupyter-client.readthedocs.io/en/latest/wrapperkernels.html
# https://github.com/jupyter/jupyter/wiki/Jupyter-kernels

import toml

from ipykernel.ipkernel import IPythonKernel
from traitlets.config.configurable import SingletonConfigurable

from icortex.services import get_service
from icortex.helper import is_prompt, extract_prompt

from icortex.config import DEFAULT_ICORTEX_CONFIG_PATH


class ICortexKernel(IPythonKernel, SingletonConfigurable):
    implementation = "ICortex"
    implementation_version = "0.0.1"
    language = "no-op"
    language_version = "0.1"
    language_info = {
        "name": "any text",
        "mimetype": "text/plain",
        "file_extension": ".py",
        "pygments_lexer": "icortex",
        "codemirror_mode": "text/plain",
    }
    banner = (
        "A prompt-based kernel for interfacing with code-generating language models"
    )

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        # TODO: pass the --config flag from icortex somehow
        config_path = DEFAULT_ICORTEX_CONFIG_PATH

        try:
            icortex_config = toml.load(config_path)
        except FileNotFoundError:
            # If config file doesn't exist, default to echo
            icortex_config = {"service": "echo", "echo": {}}

        # Initialize the Service object
        service_name = icortex_config["service"]
        service_config = icortex_config[service_name]
        service_class = get_service(service_name)
        self.service = service_class(service_config)

    async def do_execute(
        self,
        input,
        silent,
        store_history=True,
        user_expressions=None,
        allow_stdin=True,
    ):
        if is_prompt(input):
            prompt = extract_prompt(input)
            # Escape triple double quotes
            prompt = prompt.replace('"""', r"\"\"\"")
            code = f'''from icortex import eval_prompt
eval_prompt("""{prompt}""")
            '''
        else:
            code = input

        # TODO: KeyboardInterrupt does not kill coroutines, fix
        # Until then, try not to use Ctrl+C while a cell is executing
        return await IPythonKernel.do_execute(
            self,
            code,
            silent,
            store_history=store_history,
            user_expressions=user_expressions,
            allow_stdin=allow_stdin,
        )


def get_icortex_kernel() -> ICortexKernel:
    """Get the global ICortexKernel instance.

    Returns None if no ICortexKernel instance is registered.
    """
    if ICortexKernel.initialized():
        return ICortexKernel.instance()


if __name__ == "__main__":
    from ipykernel.kernelapp import IPKernelApp

    IPKernelApp.launch_instance(kernel_class=ICortexKernel)
