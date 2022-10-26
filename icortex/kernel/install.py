import os
import sys
import json
import shutil
import argparse
import pkg_resources

from IPython.utils.tempdir import TemporaryDirectory

try:
    from jupyter_client.kernelspec import KernelSpecManager

    HAVE_JUPYTER = True
except ImportError:
    HAVE_JUPYTER = False

kernel_json = {
    "argv": [sys.executable, "-m", "icortex.kernel", "-f", "{connection_file}"],
    "display_name": "ICortex",
    "language": "python",
}

KERNEL_RESOURCES = [
    "logo-svg.svg",
    "logo-32x32.png",
    "logo-64x64.png",
    "logo-128x128.png",
    "logo-256x256.png",
    "logo-512x512.png",
]


def install_my_kernel_spec(user=True, prefix=None, uninstall=False):
    if not HAVE_JUPYTER:
        print("Could not install Jupyter kernel spec, please install jupyter_client")
        return

    ksm = KernelSpecManager()
    if not uninstall:
        with TemporaryDirectory() as td:
            os.chmod(td, 0o755)  # Starts off as 700, not user readable
            with open(os.path.join(td, "kernel.json"), "w") as f:
                json.dump(kernel_json, f, sort_keys=True)

            # Copy resources such as logos
            for resource in KERNEL_RESOURCES:
                resource_path = pkg_resources.resource_filename(
                    "icortex", "kernel/icortex/" + resource
                )
                shutil.copy(resource_path, td)

            print("Installing Jupyter kernel spec")
            ksm.install_kernel_spec(td, "icortex", user=user, prefix=prefix)
    else:
        try:
            ksm.remove_kernel_spec("icortex")
        except KeyError:
            print("ICortex kernel not installed, skipping.")


def _is_root():
    try:
        return os.geteuid() == 0
    except AttributeError:
        return False  # assume not an admin on non-Unix platforms


def is_kernel_installed():
    if not HAVE_JUPYTER:
        print("Could not install Jupyter kernel spec, please install jupyter_client")
        return False

    ksm = KernelSpecManager()

    paths = ksm.find_kernel_specs()
    return "icortex" in paths


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--user",
        action="store_true",
        help="Install to the per-user kernels registry. Default if not root.",
    )
    ap.add_argument(
        "--sys-prefix",
        action="store_true",
        help="Install to sys.prefix (e.g. a virtualenv or conda env)",
    )
    ap.add_argument(
        "--prefix",
        help="Install to the given prefix. "
        "Kernelspec will be installed in {PREFIX}/share/jupyter/kernels/",
    )
    ap.add_argument("--uninstall", action="store_true", help="Uninstall kernelspec.")
    args = ap.parse_args(argv)

    if args.sys_prefix:
        args.prefix = sys.prefix
    if not args.prefix and not _is_root():
        args.user = True

    try:
        install_my_kernel_spec(
            user=args.user, prefix=args.prefix, uninstall=args.uninstall
        )
    except:
        pass


if __name__ == "__main__":
    main()
