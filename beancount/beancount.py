from datetime import date
from exchange.transaction import Transaction
from exchange.mapper import TxnToEntryMapper


class BeancountPostingEntry:
    def __init__(
        self,
        account_name: str | None = None,
        original_cost: float | None = None,
        original_cost_currency: str | None = None,
        total_cost: float | None = None,
        total_cost_currency: str | None = None,
        is_debit_transaction: bool | None = None,
    ) -> None:
        self.account_name = account_name
        self.original_cost = original_cost
        self.original_cost_currency = original_cost_currency
        self.total_cost = total_cost
        self.total_cost_currency = total_cost_currency
        self.is_debit_transaction = is_debit_transaction

    def __str__(self) -> str:
        posting_line = f"{self.account_name}"
        posting_entry = ""
        if self.original_cost and self.total_cost:
            posting_entry += f"{self.original_cost} {self.original_cost_currency} @@ {self.total_cost} {self.total_cost_currency}"
        elif self.total_cost:
            posting_entry += f"{self.total_cost} {self.total_cost_currency}"

        if posting_entry and not self.is_debit_transaction:
            posting_entry = "-" + posting_entry

        return f"{posting_line} {posting_entry}".strip()


class BeancountTxnEntry:

    def __init__(
        self,
        date: date = date.fromisocalendar(1900, 1, 1),
        flag: str | None = None,
        payee: str | None = None,
        narration: str | None = None,
    ) -> None:
        self.date = date
        self.flag = flag
        self.payee = payee
        self.narration = narration
        self.postings: list[BeancountPostingEntry] = []

    def add_posting(self, posting: BeancountPostingEntry):
        self.postings.append(posting)

    def __lt__(self, other: "BeancountTxnEntry") -> bool:
        return self.date < other.date

    def __str__(self) -> str:
        header = f"{self.date.isoformat()} {self.flag}"
        if self.payee:
            header += f' "{self.payee}"'
        if self.narration:
            header += f' "{self.narration}"'

        for posting in self.postings:
            header += f"\n\t{posting}"

        return header


class BeanCountTxnMapper(TxnToEntryMapper):

    def map_to_entry(self, txn: Transaction) -> BeancountTxnEntry:
        bc_entry = BeancountTxnEntry(
            date=txn.get_date(),
            flag="!",
            payee=txn.get_payee(),
            narration=txn.get_comments(),
        )

        for posting in txn.get_postings():
            bc_posting = BeancountPostingEntry(
                account_name=posting.get_account_name(),
                original_cost=posting.get_original_amount(),
                original_cost_currency=posting.get_original_currency(),
                total_cost=posting.get_amount_in_account_currency(),
                total_cost_currency=posting.get_account_currency(),
                is_debit_transaction=posting.get_is_debit_to_account(),
            )
            bc_entry.add_posting(bc_posting)

        return bc_entry
