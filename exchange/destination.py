from abc import ABC, abstractmethod
from typing import Any

from .transaction import Transaction


class TxnToEntryMapper(ABC):

    @abstractmethod
    def map_to_entry(self, txn: Transaction) -> Any:
        raise NotImplementedError("map_to_entry not implemented")
