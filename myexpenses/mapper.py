from . import MyExpensesEntry, MyExpensesTxn, MyExpensesPosting
from exchange.mapper import EntryToTxnMapper


class MyExpensesMapper(EntryToTxnMapper):

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
