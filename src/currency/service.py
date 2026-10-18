from collections.abc import Iterable

from sqlalchemy import select

from src import database, models
from src.currency import exceptions, schemas


def get_currency_list() -> Iterable[models.Currency]:
    stmt = select(models.Currency)
    return database.fetch_all(stmt)


def get_currency(code: str) -> models.Currency | None:
    # Codes are stored uppercase (see CurrencyCreate); lookups ignore case
    stmt = select(models.Currency).where(models.Currency.code == code.upper())
    return database.fetch_one(stmt)


def get_valid_currency(code: str) -> models.Currency:
    currency = get_currency(code)
    if not currency:
        raise exceptions.CurrencyNotFound()
    return currency


def add_currency(item: schemas.CurrencyCreate) -> models.Currency:
    db_item = models.Currency(**item.model_dump())
    return database.upd_one(db_item)
