from datetime import datetime
from unittest import TestCase

from stockplot import DeGiroWrapper, Transaction
from stockplot.de_giro_wrapper.degiro_container import de_giro_factory_service
from stockplot.requests_wrapper.requests_service import requests_service
from .utils import get_login_request, get_client_info_request, get_logout_request
from ...mock_packages.mock_requests import (
    MockJsonResponse,
    MockTraffic,
    RequestMethod,
    MockRequests,
)

__all__ = ("TestGetTransactions",)


class TestGetTransactions(TestCase):
    _dict_padding = {
        "id": 1,
        "buysell": "B",
        "price": 1,
        "total": -1,
        "orderTypeId": 0,
        "counterParty": "MK",
        "transfered": False,
        "fxRate": 1,
        "totalInBaseCurrency": -1,
        "feeInBaseCurrency": -1,
        "totalPlusFeeInBaseCurrency": -1,
        "transactionTypeId": 0,
        "tradingVenue": "XET",
    }

    def _set_requests(
        self,
        data: MockTraffic,
        user: str = "user",
        password: str = "pass",
        account_id: int = 0,
        session_id: str = "session_id",
    ) -> None:
        traffic = [
            get_login_request(user, password, session_id),
            get_client_info_request(session_id, account_id),
            data,
            get_logout_request(session_id, account_id),
        ]

        requests_service.overwrite(new=lambda: MockRequests(expected_traffic=traffic))

    def _start_test(self, user: str = "user", password: str = "pass") -> DeGiroWrapper:
        factory = de_giro_factory_service.get()
        return factory().create(user=user, password=password)

    def tearDown(self) -> None:
        requests_service.reset()

    def test_happy_path(self) -> None:
        raw_data = [
            {"productId": 1, "quantity": 1, "date": "1970-01-01T01:00:00+01:00"},
            {"productId": 1, "quantity": -1, "date": "1970-01-01T01:00:01+01:00"},
        ]

        mock_response = MockJsonResponse(status_code=200, _json={"data": raw_data})

        start_date = datetime(1970, 1, 1)
        end_date = datetime(1970, 1, 1)

        self._set_requests(
            data=MockTraffic(
                method=RequestMethod.GET,
                args=tuple(),
                kwargs={
                    "url": "https://trader.degiro.nl/reporting/secure/v4/transactions",
                    "params": {
                        "fromDate": start_date.strftime("%d/%m/%Y"),
                        "toDate": end_date.strftime("%d/%m/%Y"),
                        "group_transactions_by_order": False,
                        "intAccount": 0,
                        "sessionId": "session_id",
                    },
                },
                response=mock_response,
            )
        )

        expected = [
            Transaction(
                product_id=1,
                quantity=1,
                transaction_datetime=datetime(1970, 1, 1, 0, 0, 0),
            ),
            Transaction(
                product_id=1,
                quantity=-1,
                transaction_datetime=datetime(1970, 1, 1, 0, 0, 1),
            ),
        ]

        with self._start_test() as de_giro:
            actual = de_giro.get_transactions(start_date=start_date, end_date=end_date)

        self.assertEquals(expected, actual)
