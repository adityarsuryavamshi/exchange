from myexpenses.parser import MyExpenseFileDetails, MyExpensesParser
from myexpenses.mapper import MyExpensesMapper
from beancount.beancount import BeanCountTxnMapper

from exchange.parser import EntryParser
from exchange.mapper import TxnToEntryMapper, EntryToTxnMapper
from typing import Any

import json


class GenericConverter:
    def __init__(
        self,
        parser: EntryParser,
        entry_to_txn_mapper: EntryToTxnMapper,
        txn_to_entry_mapper: TxnToEntryMapper,
    ) -> None:
        self.parser = parser
        self.entry_to_txn_mapper = entry_to_txn_mapper
        self.txn_to_entry_mapper = txn_to_entry_mapper

    def convert(self) -> list[Any]:
        converted_entries: list[Any] = []
        for entry_a in self.parser:
            txn = self.entry_to_txn_mapper.map_to_txn(entry_a)
            converted_entry = self.txn_to_entry_mapper.map_to_entry(txn)
            converted_entries.append(converted_entry)
        converted_entries.sort()
        return converted_entries

if __name__ == "__main__":
    conf_json = ""
    with open("my_expenses_conf.json") as f:
        conf_json = json.load(f)
    csv_field_mappings = conf_json["csv_field_mappings"]
    json_field_mappings = conf_json["json_field_mappings"]
    category_account_mapping = conf_json["category_account_mapping"]

    export_file_details = conf_json["files"]
    my_expense_file_details = []
    for efd in export_file_details:
        file_path = efd["file_path"] 
        file_type = efd["file_type"]
        date_format = efd["date_format"]
        account = efd["account"]
        account_currency = efd["account_currency"]

        field_mappings = csv_field_mappings if file_type == "CSV" else json_field_mappings

        file_detail = MyExpenseFileDetails(file_path, file_type, field_mappings, date_format, account, account_currency)

        my_expense_file_details.append(file_detail)
    
    my_expense_parser = MyExpensesParser(my_expense_file_details)
    my_expense_mapper = MyExpensesMapper(category_account_mapping)
    bean_count_mapper = BeanCountTxnMapper()

    converter = GenericConverter(my_expense_parser, my_expense_mapper, bean_count_mapper)
    bc_entries = converter.convert()
    
    for entry in bc_entries:
        print(entry)
        print()

