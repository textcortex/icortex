# Guides to writing Jupyter kernels:
# https://jupyter-client.readthedocs.io/en/latest/wrapperkernels.html
# https://github.com/jupyter/jupyter/wiki/Jupyter-kernels

import typing as t

from ipykernel.ipkernel import IPythonKernel
from traitlets.config.configurable import SingletonConfigurable

from icortex.helper import extract_cli, is_cli, is_prompt, extract_prompt, escape_quotes
from icortex.services import ServiceBase


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
        self.service = None
        # self.set_service()

    async def do_execute(
        self,
        input_,
        silent,
        store_history=True,
        user_expressions=None,
        allow_stdin=True,
    ):
        if is_cli(input_):
            prompt = extract_cli(input_)
            prompt = escape_quotes(prompt)
            code = f'''from icortex import eval_cli
eval_cli("""{prompt}""")
'''
        elif is_prompt(input_):
            prompt = extract_prompt(input_)
            prompt = escape_quotes(prompt)

            if self.service is None:
                code = f'''from icortex import set_icortex_service, eval_prompt
success = set_icortex_service()
if success:
    code = eval_prompt("""{prompt}""")
    exec(code)
else:
    print(\'No service selected. Run `//service init` to initialize a service.\')
'''
            else:
                code = f'''from icortex import eval_prompt
code = eval_prompt("""{prompt}""")
exec(code)'''
        else:
            code = input_

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

    def set_service(self, service: t.Type[ServiceBase]):
        self.service = service
        return True


def get_icortex_kernel() -> ICortexKernel:
    """Get the global ICortexKernel instance.

    Returns None if no ICortexKernel instance is registered.
    """
    if ICortexKernel.initialized():
        return ICortexKernel.instance()


def print_help() -> None:
    icortex_kernel = get_icortex_kernel()
    if icortex_kernel is not None:
        icortex_kernel.service.prompt_parser.print_help()


if __name__ == "__main__":
    from ipykernel.kernelapp import IPKernelApp

    IPKernelApp.launch_instance(kernel_class=ICortexKernel)
