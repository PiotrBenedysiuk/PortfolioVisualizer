from . import DeGiroWrapper
from stockplot.requests_wrapper.requests_protocol import RequestsProtocol

__all__ = ('DeGiroFactory',)


class DeGiroFactory:

    def __init__(self, requests: RequestsProtocol) -> None:
        self._requests = requests

    def create(
        self,
        user: str,
        password: str
    ) -> DeGiroWrapper:
        return DeGiroWrapper(
            user=user,
            password=password,
            requests=self._requests
        )
