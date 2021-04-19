import json
import typing
from datetime import datetime
from unittest import TestCase

from stockplot import DeGiroWrapper, Transaction, ProductInfo, Currency
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
        "contractSize": 1.0,
        "productType": "STOCK",
        "productTypeId": 1,
        "tradable": True,
        "category": "D",
        "exchangeId": "1",
        "onlyEodPrices": False,
        "orderTimeTypes": ["DAY", "GTC"],
        "buyOrderTypes": ["LIMIT", "MARKET", "STOPLOSS", "STOPLIMIT"],
        "sellOrderTypes": ["LIMIT", "MARKET", "STOPLOSS", "STOPLIMIT"],
        "productBitTypes": [],
        "closePrice": 1.0,
        "closePriceDate": "2021-04-16",
        "feedQuality": "D15",
        "orderBookDepth": 0,
        "vwdIdentifierType": "issueid",
        "vwdId": "1",
        "qualitySwitchable": True,
        "qualitySwitchFree": False,
        "vwdModuleId": 1,
    }

    def _set_requests(
        self,
        data: MockJsonResponse,
        ids: typing.Set[int],
        user: str = "user",
        password: str = "pass",
        account_id: int = 0,
        session_id: str = "session_id",
    ) -> None:
        traffic = [
            get_login_request(user, password, session_id),
            get_client_info_request(session_id, account_id),
            MockTraffic(
                method=RequestMethod.POST,
                args=tuple(),
                kwargs={
                    "url": "https://trader.degiro.nl/product_search/secure/v5/products/info",
                    "headers": {"content-type": "application/json"},
                    "params": {
                        "intAccount": account_id,
                        "sessionId": session_id,
                    },
                    "data": json.dumps(list(ids)),
                },
                response=data,
            ),
            get_logout_request(session_id, account_id),
        ]

        requests_service.overwrite(new=lambda: MockRequests(expected_traffic=traffic))

    def _start_test(self, user: str = "user", password: str = "pass") -> DeGiroWrapper:
        factory = de_giro_factory_service.get()
        return factory().create(user=user, password=password)

    def tearDown(self) -> None:
        requests_service.reset()

    def test_happy_path(self) -> None:
        raw_data = {
            "id": "1",
            "isin": "123",
            "name": "Koninklijke Porceleyne Fles NV",
            "symbol": "PORF",
            "currency": "EUR",
            **self._dict_padding,
        }

        mock_response = MockJsonResponse(
            status_code=200, _json={"data": {"1": raw_data}}
        )

        ids = {1}

        self._set_requests(data=mock_response, ids=ids)

        expected = {
            1: ProductInfo(
                id=1,
                isin="123",
                name="Koninklijke Porceleyne Fles NV",
                symbol="PORF",
                currency=Currency.EUR,
            )
        }

        with self._start_test() as de_giro:
            actual = de_giro.get_product_info_by_id(ids=ids)

        self.assertEqual(expected, actual)

    def test_missing_id(self) -> None:
        raw_data = {
            "id": "1",
            "isin": "123",
            "name": "Koninklijke Porceleyne Fles NV",
            "symbol": "PORF",
            "currency": "EUR",
            **self._dict_padding,
        }

        mock_response = MockJsonResponse(
            status_code=200, _json={"data": {"1": raw_data}}
        )

        ids = {1, 999999999}

        self._set_requests(data=mock_response, ids=ids)

        expected = {
            1: ProductInfo(
                id=1,
                isin="123",
                name="Koninklijke Porceleyne Fles NV",
                symbol="PORF",
                currency=Currency.EUR,
            )
        }

        with self._start_test() as de_giro:
            actual = de_giro.get_product_info_by_id(ids=ids)

        self.assertEqual(expected, actual)

    def test_only_missing_id(self) -> None:
        mock_response = MockJsonResponse(status_code=200, _json={})

        ids = {999999999}

        self._set_requests(data=mock_response, ids=ids)

        with self.assertRaises(expected_exception=Exception) as context:
            with self._start_test() as de_giro:
                actual = de_giro.get_product_info_by_id(ids=ids)

        expected_msg = f"No products found with ids {ids}."

        self.assertEqual(expected_msg, str(context.exception))
