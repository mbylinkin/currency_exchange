from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src import models, database
from src.exchange_rate import schemas

from src.currency import service as currency_service

from src.utils import parse_currency_pair


def get_exc_rate_list() -> Iterable[models.ExchangeRates]:
    stmt = select(models.ExchangeRates).options(
        joinedload(models.ExchangeRates.base_currency, innerjoin="unnested"),
        joinedload(models.ExchangeRates.target_currency, innerjoin="unnested"),
    )
    return database.fetch_all(stmt)


def get_exc_rate(code: str) -> models.ExchangeRates:
    base_val_code, target_val_code = parse_currency_pair(code)

    stmt = select(models.ExchangeRates).options(
        joinedload(
            models.ExchangeRates.base_currency.and_(
                models.Currency.code == base_val_code
            ),
            innerjoin="unnested",
        ),
        joinedload(
            models.ExchangeRates.target_currency.and_(
                models.Currency.code == target_val_code
            ),
            innerjoin="unnested",
        ),
    )
    return database.fetch_one(stmt)


def add_exc_rate(item: schemas.ExchangeRateCreate) -> models.ExchangeRates:
    base_currency = currency_service.get_valid_currency(item.base_currency_code)
    target_currency = currency_service.get_valid_currency(item.target_currency_code)
    db_item = models.ExchangeRates(
        base_currency=base_currency, target_currency=target_currency, rate=item.rate
    )
    return database.upd_one(db_item)


def upd_exc_rate(code: str, item: schemas.ExchangeRateUpdate) -> models.ExchangeRates:
    db_item = get_exc_rate(code)
    data_dict = item.model_dump(exclude_unset=True)
    for key, value in data_dict.items():
        setattr(db_item, key, value)
    return database.upd_one(db_item)
