from . import BeancountTxnEntry, BeancountPostingEntry

from exchange.destination import TxnToEntryMapper
from exchange.transaction import Transaction


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
