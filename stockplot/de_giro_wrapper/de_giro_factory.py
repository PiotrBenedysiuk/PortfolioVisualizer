from typing import Callable

from . import DeGiroWrapper
from stockplot.requests_wrapper.requests_protocol import RequestsProtocol

__all__ = ("DeGiroFactory",)


class DeGiroFactory:
    def __init__(self, requests_factory: Callable[[], RequestsProtocol]) -> None:
        self._requests_factory = requests_factory

    def create(self, user: str, password: str) -> DeGiroWrapper:
        return DeGiroWrapper(
            user=user, password=password, requests=self._requests_factory()
        )
