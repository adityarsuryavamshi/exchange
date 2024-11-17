import json
from datetime import datetime
from ..my_expenses import MyExpensesEntry

class JSONReader:
    __DATE = "DATE"
    __PAYEE = "PAYEE"
    __AMOUNT = "AMOUNT"
    __CATEGORY = "CATEGORY"
    __NOTES = "NOTES"
    __ID = "ID"
    __TRANSFER_ACCOUNT = "TRANSFER_ACCOUNT"

    def __init__(
        self,
        file_path: str,
        field_mapping: dict[str, str],
        date_format: str,
        account: str,
        account_currency: str,
    ) -> None:
        self.file_path = file_path
        self.field_mapping = field_mapping
        self.date_format = date_format
        self.account = account
        self.account_currency = account_currency
        self.reader = None

    def __get_my_expenses_txn(self, json_txn):
        id = json_txn.get(self.field_mapping[self.__ID], "").strip()
        date_str = json_txn.get(self.field_mapping[self.__DATE], "").strip()
        payee = json_txn.get(self.field_mapping[self.__PAYEE], "").strip()
        amount = float(json_txn.get(self.field_mapping[self.__AMOUNT], 0))
        category = json_txn.get(self.field_mapping[self.__CATEGORY], [])
        notes = json_txn.get(self.field_mapping[self.__NOTES], "").strip()

        transfer_account = json_txn.get(
            self.field_mapping[self.__TRANSFER_ACCOUNT], ""
        ).strip()
        if transfer_account:
            # In JSON format, a transfer is indidcated by the presence of the transferAccount key
            # as well as a "Transfer" category in the category.
            # In CSV format, transfer is indicated by just the account name in square brackets in category
            # since the category is used to identify the account everywhere, it makes sense to override the
            # category here and set it to the transferring account.
            category = [f"[{transfer_account}]"]

        is_income = True if amount > 0 else False

        txn_date = datetime.fromisocalendar(1900, 1, 1).date()
        if date_str:
            txn_date = datetime.strptime(date_str, self.date_format).date()

        concatted_category = " > ".join(
            category
        )  # To ensure consistency between this and CSV categories

        return MyExpensesEntry(
            id=id,
            source_account=self.account,
            source_account_currency=self.account_currency,
            date=txn_date,
            payee=payee,
            notes=notes,
            is_income=is_income,
            category=concatted_category,
            amount_in_src_account_currency=abs(
                amount
            ),  # The amount should be absolute since we are using is_income to determine if it's income or expense to this account
        )

    def __iter__(self):
        with open(self.file_path) as f:
            exported_json = json.load(f)
        self.json_txns = exported_json.get("transactions", [])
        self.txn_count = 0
        self.total_txns = len(self.json_txns)
        return self

    def __next__(self):
        if self.txn_count >= self.total_txns:
            raise StopIteration

        next_txn = self.json_txns[self.txn_count]
        self.txn_count += 1
        return self.__get_my_expenses_txn(next_txn)
