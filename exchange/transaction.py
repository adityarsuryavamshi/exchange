from abc import ABC, abstractmethod
from datetime import date


class Posting(ABC):

    @abstractmethod
    def get_account_name(self) -> str:
        raise NotImplementedError("account_name method not implemented")

    @abstractmethod
    def get_account_currency(self) -> str | None:
        raise NotImplementedError("account_currency method not implemented")

    @abstractmethod
    def get_amount_in_account_currency(self) -> float | None:
        raise NotImplementedError("amount_in_account_currency method not implemented")

    @abstractmethod
    def get_original_amount(self) -> float | None:
        return None

    @abstractmethod
    def get_original_currency(self) -> str | None:
        return None

    @abstractmethod
    def get_is_debit_to_account(self) -> bool:
        raise NotImplementedError("is_debit_to_account method not implemented")


class Transaction(ABC):

    @abstractmethod
    def get_date(self) -> date:
        raise NotImplementedError("date method not implemented")

    @abstractmethod
    def get_payee(self) -> str | None:
        raise NotImplementedError("payee method not implemented")

    @abstractmethod
    def get_comments(self) -> str | None:
        raise NotImplementedError("comments method not implemented")

    @abstractmethod
    def get_postings(self) -> list[Posting]:
        raise NotImplementedError("postings method not implemented")
