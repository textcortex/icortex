from . import *
from ipykernel.kernelapp import IPKernelApp

IPKernelApp.launch_instance(kernel_class=ICortexKernel)
