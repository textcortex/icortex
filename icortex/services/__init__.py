import typing as t
from copy import deepcopy
import importlib

from icortex.services.service_base import ServiceBase, ServiceVariable

from icortex.defaults import DEFAULT_SERVICE

#: A dictionary that maps unique service names to corresponding
#: classes that derive from :class:`icortex.services.service_base.ServiceBase`.
#: Extend this to add new code generation services to ICortex.
AVAILABLE_SERVICES: t.Dict[str, str] = {
    "echo": "icortex.services.echo.EchoService",
    "textcortex": "icortex.services.textcortex.TextCortexService",
    "openai": "icortex.services.openai.OpenAIService",
    "huggingface": "icortex.services.huggingface.HuggingFaceAutoService",
}


def get_service(name: str) -> t.Type[ServiceBase]:
    """Get the class corresponding a service name

    Args:
        name (str): Name of the service in :data:`AVAILABLE_SERVICES`

    Returns:
        Type[ServiceBase]: A class that derives from ServiceBase
    """
    path = AVAILABLE_SERVICES[name]
    module_path, service_name = path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    service = module.__dict__[service_name]
    return service


def get_available_services() -> t.List[str]:
    # sorted_services = sorted(
    #     [key for key, val in service_dict.items() if not val.hidden]
    # )
    sorted_services = list(sorted(AVAILABLE_SERVICES.keys()))
    sorted_services.remove(DEFAULT_SERVICE)
    sorted_services = [DEFAULT_SERVICE] + sorted_services

    return sorted_services
