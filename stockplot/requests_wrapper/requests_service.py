import requests

from .requests_protocol import RequestsProtocol
from ..service import Service

__all__ = ('requests_service',)


class _RequestsWrapper:
    def get(self, *args, **kwargs) -> requests.models.Response:
        return requests.get(*args, **kwargs)

    def post(self, *args, **kwargs) -> requests.models.Response:
        return requests.post(*args, **kwargs)


requests_service: Service[RequestsProtocol] = Service(
    value=_RequestsWrapper
)
