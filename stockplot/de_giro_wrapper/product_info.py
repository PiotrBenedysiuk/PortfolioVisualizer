from dataclasses import dataclass

from ..currency import Currency

__all__ = ("ProductInfo",)


@dataclass(frozen=True)
class ProductInfo:
    id: int
    isin: str
    name: str
    symbol: str
    currency: Currency
