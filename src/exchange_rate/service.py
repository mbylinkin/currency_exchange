from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.orm import aliased, contains_eager

from src import database, models
from src.currency import service as currency_service
from src.exchange_rate import exceptions, schemas
from src.utils import parse_currency_pair


def get_exc_rate_list() -> Iterable[models.ExchangeRates]:
    # Both currencies come eagerly through the model's lazy="joined"
    return database.fetch_all(select(models.ExchangeRates))


def get_exc_rate(code: str) -> models.ExchangeRates | None:
    base_code, target_code = parse_currency_pair(code.upper())
    base = aliased(models.Currency)
    target = aliased(models.Currency)

    # Filter with join + where, then fill the relationships from the same joins
    stmt = (
        select(models.ExchangeRates)
        .join(base, models.ExchangeRates.base_currency)
        .join(target, models.ExchangeRates.target_currency)
        .where(base.code == base_code, target.code == target_code)
        .options(
            contains_eager(models.ExchangeRates.base_currency.of_type(base)),
            contains_eager(models.ExchangeRates.target_currency.of_type(target)),
        )
    )
    return database.fetch_one(stmt)


def get_valid_exc_rate(code: str) -> models.ExchangeRates:
    exc_rate = get_exc_rate(code)
    if not exc_rate:
        raise exceptions.ExcRateNotFound()
    return exc_rate


def add_exc_rate(item: schemas.ExchangeRateCreate) -> models.ExchangeRates:
    base_currency = currency_service.get_valid_currency(item.base_currency_code)
    target_currency = currency_service.get_valid_currency(item.target_currency_code)
    db_item = models.ExchangeRates(
        base_currency=base_currency, target_currency=target_currency, rate=item.rate
    )
    return database.upd_one(db_item)


def upd_exc_rate(code: str, item: schemas.ExchangeRateUpdate) -> models.ExchangeRates:
    db_item = get_valid_exc_rate(code)
    data_dict = item.model_dump(exclude_unset=True)
    for key, value in data_dict.items():
        setattr(db_item, key, value)
    return database.upd_one(db_item)
