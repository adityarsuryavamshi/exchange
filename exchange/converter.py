from typing import Any, Callable

from .source import EntryParser, EntryToTxnMapper
from .destination import TxnToEntryMapper


class Converter:
    def __init__(
        self,
        parser: EntryParser,
        entry_to_txn_mapper: EntryToTxnMapper,
        txn_to_entry_mapper: TxnToEntryMapper,
    ) -> None:
        self.parser = parser
        self.entry_to_txn_mapper = entry_to_txn_mapper
        self.txn_to_entry_mapper = txn_to_entry_mapper

    def convert(
        self, sort_transactions_with_key: Callable[[Any], Any] | None = None
    ) -> list[Any]:
        converted_entries: list[Any] = []
        for entry_a in self.parser:
            txn = self.entry_to_txn_mapper.map_to_txn(entry_a)
            converted_entry = self.txn_to_entry_mapper.map_to_entry(txn)
            converted_entries.append(converted_entry)
        if sort_transactions_with_key:
            converted_entries.sort(key=sort_transactions_with_key)
        return converted_entries
