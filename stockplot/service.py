from typing import TypeVar, Optional, Callable

T = TypeVar("T")


class Service(T):
    def __init__(self, value: Callable[[], T]) -> None:
        self._value = value
        self._overloaded: Optional[Callable[[], T]] = None

    def get(self) -> T:
        if self._overloaded:
            return self._overloaded()

        return self._value()

    def overwrite(self, new: Callable[[], T]) -> None:
        self._overloaded = new

    def reset(self) -> None:
        self._overloaded = None
