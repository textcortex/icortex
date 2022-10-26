import IPython
from icortex.kernel import ICortexKernel
from ipykernel.kernelapp import IPKernelApp

IPKernelApp.launch_instance(kernel_class=ICortexKernel)
