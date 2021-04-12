import datetime
from dataclasses import dataclass

__all__ = ("Transaction",)


@dataclass(frozen=True)
class Transaction:
    product_id: int
    quantity: int
    transaction_datetime: datetime.datetime  # cue in timezone bullshit.
