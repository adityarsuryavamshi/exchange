from abc import ABC, abstractmethod
from typing import Any


class EntryParser(ABC):

    @abstractmethod
    def parse(self) -> list[Any]:
        raise NotImplementedError("parse not implemented")

    @abstractmethod
    def __iter__(self) -> "EntryParser":
        raise NotImplementedError("__iter__ not implemented")

    @abstractmethod
    def __next__(self) -> Any:
        raise NotImplementedError("__next__ not implemented")
