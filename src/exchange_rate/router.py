from collections.abc import Iterable
from typing import NoReturn

from fastapi import APIRouter, Depends, status

from src import models
from src.exceptions import AlreadyExists
from src.exchange_rate import exceptions, schemas
from src.exchange_rate.service import (
    add_exc_rate,
    get_exc_rate_list,
    get_valid_exc_rate,
    upd_exc_rate,
)

router = APIRouter()


@router.get("/exchangeRates", response_model=list[schemas.ExchangeRate])
def get_exchange_rates() -> Iterable[models.ExchangeRates]:
    return get_exc_rate_list()


@router.get(
    "/exchangeRate/", response_model=schemas.ExchangeRate, include_in_schema=False
)
def get_exchange_rate_empty_code() -> NoReturn:
    raise exceptions.NoExcRateCodeError()


@router.get("/exchangeRate/{code}", response_model=schemas.ExchangeRate)
def get_exchange_rate_by_code(code: str) -> models.ExchangeRates:
    return get_valid_exc_rate(code)


@router.post(
    "/exchangeRates",
    response_model=schemas.ExchangeRate,
    status_code=status.HTTP_201_CREATED,
)
def create_exchange_rate(
    exchange_rate_data: schemas.ExchangeRateCreate = Depends(
        schemas.ExchangeRateCreate.as_form
    ),
) -> models.ExchangeRates:
    try:
        return add_exc_rate(exchange_rate_data)
    except AlreadyExists:
        raise exceptions.ExcRateAlreadyExists()


@router.patch(
    "/exchangeRate/{code}",
    response_model=schemas.ExchangeRate,
    status_code=status.HTTP_200_OK,
)
def update_exchange_rate(
    code: str,
    exchange_rate_data: schemas.ExchangeRateUpdate = Depends(
        schemas.ExchangeRateUpdate.as_form
    ),
) -> models.ExchangeRates:
    return upd_exc_rate(code, exchange_rate_data)
