# Guides to writing Jupyter kernels:
# https://jupyter-client.readthedocs.io/en/latest/wrapperkernels.html
# https://github.com/jupyter/jupyter/wiki/Jupyter-kernels

from ipykernel.ipkernel import IPythonKernel


from .exec import is_prompt, extract_prompt


class ICortexKernel(IPythonKernel):
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


if __name__ == "__main__":
    from ipykernel.kernelapp import IPKernelApp

    IPKernelApp.launch_instance(kernel_class=ICortexKernel)
