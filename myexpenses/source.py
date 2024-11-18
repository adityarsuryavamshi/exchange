from typing import Union, Type

from .readers import CSVReader, JSONReader
from . import MyExpensesEntry, MyExpensesTxn, MyExpensesPosting

from exchange.source import EntryParser, EntryToTxnMapper


class MyExpenseFileDetails:

    def __init__(
        self,
        file_path: str,
        file_type: str,
        field_mapping: dict[str, str],
        date_format: str,
        account: str,
        account_currency: str,
    ) -> None:
        self.file_path = file_path
        self.file_type = file_type
        self.field_mapping = field_mapping
        self.date_format = date_format
        self.account = account
        self.account_currency = account_currency


class MyExpensesParser(EntryParser):

    __FILE_PARSERS: dict[str, Union[Type[CSVReader], Type[JSONReader]]] = {
        "CSV": CSVReader,
        "JSON": JSONReader,
    }

    def __init__(self, file_details: list[MyExpenseFileDetails]) -> None:
        self.file_details = file_details
        self.my_expenses_entries: list[MyExpensesEntry] = []
        self.parsed = False

    def parse(self) -> list[MyExpensesEntry]:
        parsed = self.__parse_file()
        if not parsed:
            raise RuntimeError("failed to parse files")
        self.__merge_entries()
        return self.my_expenses_entries

    def __iter__(self):
        self.parse()
        self.idx = 0
        return self

    def __next__(self):
        if self.idx >= len(self.my_expenses_entries):
            raise StopIteration
        next_entry = self.my_expenses_entries[self.idx]
        self.idx += 1
        return next_entry

    def __parse_file(self):
        for fd in self.file_details:
            file_parser_clz = self.__FILE_PARSERS.get(fd.file_type, None)
            if not file_parser_clz:
                raise NotImplementedError(
                    f"no parser defined for file type {fd.file_type}"
                )
            file_parser = file_parser_clz(
                fd.file_path,
                fd.field_mapping,
                fd.date_format,
                fd.account,
                fd.account_currency,
            )
            for entry in file_parser:
                self.my_expenses_entries.append(entry)
        return True

    def __transfer_merge(self, entries: list[MyExpensesEntry]):
        """transfer_merge only handles the case of transfers for which
        it expects just two entries one from source and another to destination"""
        if len(entries) > 2:
            return (False, None)

        # In case of transfer
        # one entry should be an income the other should be an expense
        # the from and to accounts of both them are swapped but are the same

        entry_a, entry_b = entries
        assert (
            entry_a.is_income != None
            and entry_b.is_income != None
            and entry_a.is_income != entry_b.is_income
        )

        # If all of the above is true, then this is a transfer
        # We can reduce this to either an income or expense, both are equivalent.

        income_entry = entry_a if entry_a.is_income else entry_b
        expense_entry = entry_b if income_entry == entry_a else entry_a

        merged_entry = MyExpensesEntry(
            id="M-" + str(income_entry.id) + "--" + str(expense_entry.id),
            source_account=expense_entry.source_account,
            source_account_currency=expense_entry.source_account_currency,
            date=expense_entry.date,
            payee=expense_entry.payee,
            notes=expense_entry.notes,
            is_income=expense_entry.is_income,
            category=expense_entry.category,
            amount_in_src_account_currency=expense_entry.amount_in_src_account_currency,
        )

        if (
            income_entry.source_account_currency
            != expense_entry.source_account_currency
        ):
            merged_entry.original_amount = income_entry.amount_in_src_account_currency
            merged_entry.original_amount_currency = income_entry.source_account_currency

        return (True, merged_entry)

    def __merge_entries(self):
        merged_entries: list[MyExpensesEntry] = []
        eligible_entries: list[MyExpensesEntry] = (
            []
        )  # Entry merging is only possible for entries with id

        for entry in self.my_expenses_entries:
            if entry.id:
                eligible_entries.append(entry)
            else:
                merged_entries.append(entry)  # The rest of the entries are kept as is

        entries_grouped_by_id: dict[str, list[MyExpensesEntry]] = {}
        for entry in eligible_entries:
            entries_grouped_by_id[entry.id] = entries_grouped_by_id.get(
                entry.id, []
            ) + [entry]

        for entry_id in entries_grouped_by_id:
            entries = entries_grouped_by_id[entry_id]
            if len(entries) == 1:  # There is a single entry no need to do anything
                merged_entries += entries
            else:
                ok, merged_entry = self.__transfer_merge(
                    entries
                )  # In the future for more complicated merge, we should spawn this off to a generic merger which then merges based on entries criteria
                if ok and merged_entry:
                    merged_entries.append(merged_entry)
                else:
                    # Merge failed, we just append the existing entries as is
                    merged_entries += entries

        self.my_expenses_entries = merged_entries


class MyExpensesEntryMapper(EntryToTxnMapper):

    def __init__(self, category_account_mapping: dict[str, str]) -> None:
        self.category_account_mapping = category_account_mapping

    def map_to_txn(self, entry: MyExpensesEntry) -> MyExpensesTxn:
        me_txn = MyExpensesTxn()
        me_txn.date = entry.date
        me_txn.payee = entry.payee
        me_txn.comments = entry.notes

        interacting_account = self.category_account_mapping.get(entry.category, entry.category)
        is_debit_for_interacting_account = (
            not entry.is_income
        )  # If it's a income for source account, it implies we would be *tranferring from* the interacting account, hence it would be a credit

        me_posting = MyExpensesPosting()

        me_posting.account_name = interacting_account
        me_posting.account_currency = (
            entry.source_account_currency if entry.source_account_currency else ""
        )
        me_posting.amount_in_account_currency = entry.amount_in_src_account_currency
        me_posting.original_amount = entry.original_amount
        me_posting.original_currency = entry.original_amount_currency
        me_posting.is_debit_to_account = is_debit_for_interacting_account

        me_txn.add_posting(me_posting)

        balancing_posting = MyExpensesPosting()
        balancing_posting.account_name = entry.source_account 

        me_txn.add_posting(balancing_posting)

        return me_txn