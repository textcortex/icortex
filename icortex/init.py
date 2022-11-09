import logging
from icortex.kernel import ICortexShell
import __main__

# import ipdb; ipdb.set_trace()
# If the kernel is IPython, load the magics.
if "get_icortex" in __main__.__dict__:
    logging.warning("ICortex is already initialized, skipping.")
elif "get_ipython" in __main__.__dict__ and "get_icortex" not in __main__.__dict__:
    # from icortex.magics import load_ipython_extension
    # ipython = globals()["get_ipython"]()
    ICortexShell._init_icortex_shell(__main__.get_ipython())
    # load_ipython_extension(get_ipython())
else:
    raise Exception("IPython is not available, cannot initialize ICortex.")