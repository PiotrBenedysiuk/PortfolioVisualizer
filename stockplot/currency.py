from __future__ import annotations
from enum import Enum

__all__ = ('Currency',)


class Currency(Enum):
    USD = 0
    EUR = 1

    @staticmethod
    def from_string(currency: str) -> Currency:
        if currency in {'USD', 'usd'}:
            return Currency.USD

        if currency in {'EUR', 'eur'}:
            return Currency.EUR

        raise Exception(f'Unknown currency {currency}')
