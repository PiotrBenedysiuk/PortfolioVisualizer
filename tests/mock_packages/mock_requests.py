import json
from dataclasses import dataclass
from enum import Enum
from json import JSONDecodeError
from typing import List, Dict, Tuple

from stockplot.requests_wrapper.response_protocol import ResponseProtocol

__all__ = ("MockTraffic", "MockRequests", "RequestMethod", "MockJsonResponse")


class RequestMethod(Enum):
    GET = 0
    POST = 1


@dataclass
class MockTraffic:
    args: Tuple
    kwargs: Dict
    method: RequestMethod
    response: ResponseProtocol


@dataclass
class MockJsonResponse:
    status_code: int
    _json: Dict

    def json(self) -> Dict:
        return self._json


@dataclass
class MockResponseWithoutJson:
    status_code: int

    def json(self) -> Dict:
        raise JSONDecodeError(
            "Expecting value: line 1 column 1 (char 0).", doc="", pos=0
        )


class MockRequests:
    def __init__(self, expected_traffic: List[MockTraffic]) -> None:
        self._expected_traffic = expected_traffic
        self._index = 0

    def get(self, *args, **kwargs) -> ResponseProtocol:
        return self._get(RequestMethod.GET, args, kwargs)

    def post(self, *args, **kwargs) -> ResponseProtocol:
        return self._get(RequestMethod.POST, args, kwargs)

    def _get(self, method: RequestMethod, args, kwargs) -> ResponseProtocol:
        if self._index >= len(self._expected_traffic):
            raise Exception(
                f"Expected {len(self._expected_traffic)} requests. "
                f"Last unhandled request: {self._serialize_request(method, *args, **kwargs)}"
            )

        expected_request = self._expected_traffic[self._index]
        self._index += 1

        if method != expected_request.method:
            raise Exception(
                f"Unexpected method, expected: "
                f"{self._serialize_request(expected_request.method, expected_request.args, expected_request.kwargs)},"
                f"got {self._serialize_request(method, *args, **kwargs)}"
            )

        if args != expected_request.args:
            raise Exception(
                f"Unexpected args, expected: "
                f"{self._serialize_request(expected_request.method, expected_request.args, expected_request.kwargs)},"
                f"got {self._serialize_request(method, *args, **kwargs)}"
            )

        if kwargs != expected_request.kwargs:
            raise Exception(
                f"Unexpected kwargs, expected: "
                f"{self._serialize_request(expected_request.method, expected_request.args, expected_request.kwargs)},"
                f"got {self._serialize_request(method, *args, **kwargs)}"
            )

        return expected_request.response

    def _serialize_request(self, method: RequestMethod, *args, **kwargs) -> str:
        return f'Method: "{method.name}", args: "{json.dumps(args)}", kwargs: "{json.dumps(kwargs)}".'
