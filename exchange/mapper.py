from abc import ABC, abstractmethod
from typing import Any


from .transaction import Transaction


class EntryToTxnMapper(ABC):

    @abstractmethod
    def map_to_txn(self, entry: Any) -> Transaction:
        raise NotImplementedError("map_to_txn not implemented")


class TxnToEntryMapper(ABC):

    @abstractmethod
    def map_to_entry(self, txn: Transaction) -> Any:
        raise NotImplementedError("map_to_entry not implemented")
