from . import BeancountTxnEntry, BeancountPostingEntry

from exchange.destination import TxnToEntryMapper
from exchange.transaction import Transaction

from myexpenses import MyExpensesTxn


class BeanCountTxnMapper(TxnToEntryMapper):

    def map_to_entry(self, txn: Transaction) -> BeancountTxnEntry:
        if isinstance(txn, MyExpensesTxn):
            return self.__map_my_expenses_txn_to_entry(txn)
        else:
            return self.__map_basic_txn(txn)
            

    def __map_basic_txn(self, txn: Transaction) -> BeancountTxnEntry:
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
        

    def __map_my_expenses_txn_to_entry(self, txn: MyExpensesTxn) -> BeancountTxnEntry:
        bc_entry = self.__map_basic_txn(txn)
        bc_entry.tags = txn.tags
        return bc_entry