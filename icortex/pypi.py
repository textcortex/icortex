import re
import importlib
import pip
import typing as t

# A dictionary of popular module names mapped to their corresponding PyPI packages.
# TODO: replace this with something more streamlined
MODULES_TO_PACKAGES = {
    "numpy": "numpy",
    "scipy": "scipy",
    "sklearn": "sklearn",
    "matplotlib": "matplotlib",
    "pandas": "pandas",
    "ethereumetl": "ethereum-etl",
}


def module_to_pypi_package(module_name):
    if module_name in MODULES_TO_PACKAGES:
        return MODULES_TO_PACKAGES[module_name]
    else:
        return None


def module_exists(name):
    spec = importlib.util.find_spec(name)
    return spec is not None


def get_imported_modules(code):
    regex = re.compile(r"^\s*(?:from|import)\s+(\w+(?:\s*,\s*\w+)*)", re.MULTILINE)
    modules = re.findall(regex, code)
    return modules


def get_missing_modules(code: str) -> t.List[str]:
    imported_modules = get_imported_modules(code)

    missing_modules = [
        module for module in imported_modules if not module_exists(module)
    ]
    return list(set(missing_modules))


def install_missing_packages(code):
    missing_modules = get_missing_modules(code)

    unresolved_modules = []
    for module in missing_modules:
        package = module_to_pypi_package(module)
        if package is not None:
            result = pip.main(["install", package])
            if result != 0:
                unresolved_modules.append(module)
        else:
            unresolved_modules.append(module)

    return unresolved_modules
