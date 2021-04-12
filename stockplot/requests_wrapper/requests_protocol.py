from typing import Protocol

from .response_protocol import ResponseProtocol

__all__ = ("RequestsProtocol",)


class RequestsProtocol(Protocol):
    def get(self, *args, **kwargs) -> ResponseProtocol:
        ...

    def post(self, *args, **kwargs) -> ResponseProtocol:
        ...
