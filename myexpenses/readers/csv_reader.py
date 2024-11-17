import csv
from datetime import datetime
from ..my_expenses import MyExpensesEntry


class CSVReader:
    __DATE = "DATE"
    __PAYEE = "PAYEE"
    __INCOME = "INCOME"
    __EXPENSE = "EXPENSE"
    __CATEGORY = "CATEGORY"
    __NOTES = "NOTES"

    def __init__(
        self,
        file_path: str,
        field_mapping: dict[str, str],
        date_format: str,
        account: str,
        account_currency: str,
    ) -> None:
        self.filePath = file_path
        self.fieldMapping = field_mapping
        self.date_format = date_format
        self.account = account
        self.account_currency = account_currency
        self.reader = None

    def __get_my_expenses_txn(self, entry_line: dict[str, str]) -> MyExpensesEntry:
        date_str = entry_line.get(self.fieldMapping[self.__DATE], "").strip()
        payee = entry_line.get(self.fieldMapping[self.__PAYEE], "").strip()
        income = float(entry_line.get(self.fieldMapping[self.__INCOME], "0").strip())
        expense = float(entry_line.get(self.fieldMapping[self.__EXPENSE], "0").strip())
        category = entry_line.get(self.fieldMapping[self.__CATEGORY], "").strip()
        notes = entry_line.get(self.fieldMapping[self.__NOTES], "").strip()

        is_income = income != 0 and expense == 0
        amount = income if is_income else expense

        txn_date = datetime.fromisocalendar(1900, 1, 1).date()
        if date_str:
            txn_date = datetime.strptime(date_str, self.date_format).date()

        return MyExpensesEntry(
            source_account=self.account,
            date=txn_date,
            payee=payee,
            notes=notes,
            is_income=is_income,
            category=category,
            amount_in_src_account_currency=amount,
            source_account_currency=self.account_currency,
        )

    def __iter__(self):
        self.f = open(self.filePath)
        self.reader = csv.DictReader(self.f)
        return self

    def __next__(self):
        line = next(self.reader, False)
        if line:
            return self.__get_my_expenses_txn(line)
        else:
            self.f.close()
            raise StopIteration
