from IPython.core.magic import (
    Magics,
    magics_class,
    line_magic,
    cell_magic,
    line_cell_magic,
)

from icortex.kernel import get_icortex, print_service_help


@magics_class
class ICortexMagics(Magics):
    @line_magic
    def help(self, line):
        print_service_help()
        return

    @line_magic
    def var(self, line):
        "Define a variable"
        shell = get_icortex()
        return shell.eval_var(line)

    @line_magic
    def export(self, line):
        "Export ICortex notebook"
        shell = get_icortex()
        return shell.export(line)

    @line_magic
    def bake(self, line):
        "Bake ICortex notebook"
        shell = get_icortex()
        return shell.bake(line)

    @line_magic
    def icortex(self, line):
        shell = get_icortex()
        return shell.cli(line)

    @line_cell_magic
    def prompt(self, line, cell=None):
        if cell is None:
            return self._prompt(line)
        else:
            return self._prompt(line + " " + cell)

    @line_cell_magic
    def p(self, line, cell=None):
        "Alias for prompt()"
        return self.prompt(line, cell=cell)

    def _prompt(self, input_):
        shell = get_icortex()
        return shell.prompt(input_)


def load_ipython_extension(ipython):
    "Register magics for ICortex"
    ipython.register_magics(ICortexMagics)
