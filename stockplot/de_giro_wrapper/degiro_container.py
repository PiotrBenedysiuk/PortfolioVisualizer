from .de_giro_factory import DeGiroFactory
from ..requests_wrapper.requests_service import requests_service
from ..service import Service

__all__ = ("de_giro_factory_service",)


def _get_factory() -> DeGiroFactory:
    requests = requests_service.get()
    return DeGiroFactory(requests=requests)


de_giro_factory_service: Service[DeGiroFactory] = Service(value=_get_factory)
