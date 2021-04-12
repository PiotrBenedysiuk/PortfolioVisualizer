from __future__ import annotations

import datetime
import json
import typing

import pytz

from .product_info import ProductInfo
from .transaction import Transaction
from ..currency import Currency
from stockplot.requests_wrapper.requests_protocol import RequestsProtocol

__all__ = ('DeGiroWrapper',)


class DeGiroWrapper:
    _LOGIN_URL = 'https://trader.degiro.nl/login/secure/login'
    _CLIENT_INFO_URL = 'https://trader.degiro.nl/pa/secure/client'
    _LOGOUT_URL = 'https://trader.degiro.nl/trading/secure/logout'

    _TRANSACTIONS_URL = 'https://trader.degiro.nl/reporting/secure/v4/transactions'
    _PRODUCT_INFO_URL = 'https://trader.degiro.nl/product_search/secure/v5/products/info'

    def __init__(
        self,
        user: str,
        password: str,
        requests: RequestsProtocol
    ) -> None:
        self._user = user
        self._password = password
        self._requests = requests
        self._session_id: typing.Optional[str] = None
        self._account_id: typing.Optional[int] = None

    def __enter__(self) -> DeGiroWrapper:
        self._login()
        self._get_client_info()
        return self

    def _login(self) -> None:
        json_params = {
            'username': self._user,
            'password': self._password,
            'isPassCodeReset': False,
            'isRedirectToMobile': False
        }
        response = self._requests.post(
            url=DeGiroWrapper._LOGIN_URL,
            json=json_params
        )
        self._session_id = response.json()['sessionId']

    def _get_client_info(self) -> None:
        response = self._requests.get(
            url=DeGiroWrapper._CLIENT_INFO_URL,
            params={'sessionId': self._session_id}
        )
        self._account_id = response.json()['data']['intAccount']

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._logout()

    def _logout(self) -> None:
        logout_params = {
            'intAccount': self._account_id,
            'sessionId': self._session_id
        }
        self._requests.get(
            url=f'{DeGiroWrapper._LOGOUT_URL};jsessionid={self._session_id}',
            params=logout_params
        )

    def get_transactions(
        self,
        start_date: datetime.datetime,
        end_date: datetime.datetime
    ) -> typing.List[Transaction]:
        transactions_parameters = {
            'fromDate': start_date.strftime('%d/%m/%Y'),
            'toDate': end_date.strftime('%d/%m/%Y'),
            'group_transactions_by_order': False,
            'intAccount': self._account_id,
            'sessionId': self._session_id
        }

        transaction_response = self._requests.get(
            url=DeGiroWrapper._TRANSACTIONS_URL,
            params=transactions_parameters
        )
        return [
            Transaction(
                product_id=transaction['productId'],
                quantity=transaction['quantity'],
                transaction_datetime=datetime.datetime.strptime(
                    transaction['date'],
                    '%Y-%m-%dT%H:%M:%S%z'
                ).astimezone(pytz.utc).replace(tzinfo=None)
            ) for transaction in transaction_response.json()['data']
        ]

    def get_product_info_by_id(
        self,
        ids: typing.Set[int]
    ) -> typing.Dict[int, ProductInfo]:
        product_info_parameters = {
            'intAccount': self._account_id,
            'sessionId': self._session_id
        }
        headers = {'content-type': 'application/json'}
        serialized_ids = json.dumps(list(ids))

        product_info_response = self._requests.post(
            url=DeGiroWrapper._PRODUCT_INFO_URL,
            headers=headers,
            params=product_info_parameters,
            data=serialized_ids
        )

        return {
            int(identifier): ProductInfo(
                id=int(product['id']),
                isin=product['isin'],
                name=product['name'],
                symbol=product['symbol'],
                currency=Currency.from_string(product['currency'])
            ) for identifier, product in
            product_info_response.json()['data'].items()
        }

