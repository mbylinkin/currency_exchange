from typing import Iterable

from sqlalchemy import select


from src import models
from src.currency import schemas
from src.currency import exceptions

from src import database


def get_currency_list() -> Iterable[models.Currency]:
    stmt = select(models.Currency)
    return database.fetch_all(stmt)


def get_currency(code: str) -> models.Currency:
    stmt = select(models.Currency).where(models.Currency.code == code)
    return database.fetch_one(stmt)


def get_valid_currency(code: str) -> models.Currency:
    currency = get_currency(code)
    if not currency:
        raise exceptions.CurrencyNotFound()
    return currency


def add_currency(item: schemas.CurrencyCreate) -> models.Currency:
    db_item = models.Currency(**item.model_dump())
    return database.upd_one(db_item)
