from myexpenses.source import (
    MyExpenseFileDetails,
    MyExpensesParser,
    MyExpensesEntryMapper,
)
from beancount.destination import BeanCountTxnMapper
from beancount import BeancountTxnEntry
from exchange.converter import Converter

import json
import argparse


def main(conf_file_path: str):
    conf_json = ""

    with open(conf_file_path) as f:
        conf_json = json.load(f)

    csv_field_mappings = conf_json["csv_field_mappings"]
    json_field_mappings = conf_json["json_field_mappings"]
    category_account_mapping = conf_json["category_account_mapping"]

    export_file_details = conf_json["files"]
    my_expense_file_details: list[MyExpenseFileDetails] = []
    for efd in export_file_details:
        file_path = efd["file_path"]
        file_type = efd["file_type"]
        date_format = efd["date_format"]
        account = efd["account"]
        account_currency = efd["account_currency"]

        field_mappings = (
            csv_field_mappings if file_type == "CSV" else json_field_mappings
        )

        file_detail = MyExpenseFileDetails(
            file_path, file_type, field_mappings, date_format, account, account_currency
        )

        my_expense_file_details.append(file_detail)

    my_expense_parser = MyExpensesParser(my_expense_file_details)
    my_expense_mapper = MyExpensesEntryMapper(category_account_mapping)
    bean_count_mapper = BeanCountTxnMapper()
    converter = Converter(my_expense_parser, my_expense_mapper, bean_count_mapper)
    bc_entries = converter.convert(sort_transactions_with_key=lambda entry: entry.date)
    for entry in bc_entries:
        print(entry)
        print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="exchange is a financial transaction mapper"
    )
    parser.add_argument("conf_file_path", type=str, help="path to configuration file")
    args = parser.parse_args()

    conf_file_path = args.conf_file_path
    main(conf_file_path)
