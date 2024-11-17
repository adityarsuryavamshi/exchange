from datetime import datetime, date
from exchange.transaction import Transaction, Posting


class MyExpensesEntry:

    def __init__(
        self,
        id: str | None = None,
        source_account: str | None = None,
        source_account_currency: str | None = None,
        date: date = date.fromisocalendar(1900, 1, 1),
        payee: str | None = None,
        notes: str | None = None,
        is_income: bool | None = None,
        category: str | None = None,
        amount_in_src_account_currency: float | None = None,
        original_amount: float | None = None,
        original_amount_currency: str | None = None,
    ) -> None:
        self.id = id
        self.source_account = source_account
        self.date = date
        self.payee = payee  # Payee is one who is receiving the money, payer is the one making the payment
        self.notes = notes
        self.is_income = is_income
        self.category = category

        self.amount_in_src_account_currency = amount_in_src_account_currency
        self.source_account_currency = source_account_currency

        self.original_amount = original_amount
        self.original_amount_currency = original_amount_currency

    def __str__(self) -> str:
        """Used primarily for debugging."""
        expense_entry_line = f'{self.id if self.id else ""}'
        expense_entry_line += f'{self.date.isoformat()} {"I" if self.is_income else "E"} "{self.payee}" "{self.notes}"\n'
        expense_entry_line += f'{f"{self.source_account} -> {self.category}" if not self.is_income else f"{self.category} -> {self.source_account}"}'

        if self.original_amount and self.original_amount_currency:
            expense_entry_line += (
                f" {self.original_amount} {self.original_amount_currency}"
            )
            if self.amount_in_src_account_currency and self.source_account_currency:
                expense_entry_line += f" @@ {self.amount_in_src_account_currency} {self.source_account_currency}"

        else:
            expense_entry_line += (
                f" {self.amount_in_src_account_currency} {self.source_account_currency}"
            )

        expense_entry_line += "\n"
        return expense_entry_line


class MyExpensesPosting(Posting):
    def __init__(self) -> None:
        self.account_name: str = ""
        self.account_currency: str | None = ""
        self.amount_in_account_currency: float | None = 0
        self.original_amount: float | None = 0
        self.original_currency: str | None = ""
        self.is_debit_to_account = True

    def get_account_name(self) -> str:
        return self.account_name

    def get_account_currency(self) -> str | None:
        return self.account_currency

    def get_amount_in_account_currency(self) -> float | None:
        return self.amount_in_account_currency

    def get_original_amount(self) -> float | None:
        return self.original_amount

    def get_original_currency(self) -> str | None:
        return self.original_currency

    def get_is_debit_to_account(self) -> bool:
        return self.is_debit_to_account


class MyExpensesTxn(Transaction):

    def __init__(self) -> None:
        self.date = datetime.fromisocalendar(1900, 1, 1).date()
        self.payee: str | None = ""
        self.comments: str | None = ""
        self.postings: list[Posting] = []

    def add_posting(self, posting: MyExpensesPosting):
        self.postings.append(posting)

    def get_date(self) -> date:
        return self.date

    def get_payee(self) -> str | None:
        return self.payee

    def get_comments(self) -> str | None:
        return self.comments

    def get_postings(self) -> list[Posting]:
        return self.postings
