from jupyter_console.app import ZMQTerminalIPythonApp


# Jupyter devs did not make this easy
# TODO: Make less hacky
class ZMQTerminalICortexApp(ZMQTerminalIPythonApp):
    def parse_command_line(self, argv=None):
        argv = ["--kernel", "icortex"]
        super(ZMQTerminalIPythonApp, self).parse_command_line(argv)
        self.build_kernel_argv(self.extra_args)
