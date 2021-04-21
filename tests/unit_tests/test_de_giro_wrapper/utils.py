from ...mock_packages.mock_requests import (
    MockJsonResponse,
    MockTraffic,
    RequestMethod,
    MockResponseWithoutJson,
)

__all__ = ("get_login_request", "get_logout_request", "get_client_info_request")


def get_login_request(
    user: str, password: str, predefined_session_id: str
) -> MockTraffic:
    response = MockJsonResponse(
        status_code=200,
        _json={
            "isPassCodeEnabled": True,
            "locale": "nl_NL",
            "redirectUrl": "https://test.testinio.nl/",
            "sessionId": predefined_session_id,
            "status": 0,
            "statusText": "success",
        },
    )
    return MockTraffic(
        method=RequestMethod.POST,
        args=tuple(),
        kwargs={
            "url": "https://trader.degiro.nl/login/secure/login",
            "json": {
                "username": user,
                "password": password,
                "isPassCodeReset": False,
                "isRedirectToMobile": False,
            },
        },
        response=response,
    )


def get_client_info_request(session_id: str, predefined_account_id: int) -> MockTraffic:
    response = MockJsonResponse(
        status_code=200,
        _json={
            "data": {  # does NOT include all of the data
                "id": 1,
                "intAccount": predefined_account_id,
            }
        },
    )
    return MockTraffic(
        method=RequestMethod.GET,
        args=tuple(),
        kwargs={
            "url": "https://trader.degiro.nl/pa/secure/client",
            "params": {"sessionId": session_id},
        },
        response=response,
    )


def get_logout_request(session_id: str, account_id: int) -> MockTraffic:
    url = f"https://trader.degiro.nl/trading/secure/logout;jsessionid={session_id}"
    response = MockResponseWithoutJson(status_code=200)
    return MockTraffic(
        method=RequestMethod.GET,
        args=(),
        kwargs={
            "url": url,
            "params": {"intAccount": account_id, "sessionId": session_id},
        },
        response=response,
    )
