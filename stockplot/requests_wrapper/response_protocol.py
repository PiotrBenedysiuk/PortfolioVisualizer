from typing import Protocol, Dict

__all__ = ("ResponseProtocol",)


class ResponseProtocol(Protocol):
    status_code: int

    def json(self) -> Dict:
        ...
