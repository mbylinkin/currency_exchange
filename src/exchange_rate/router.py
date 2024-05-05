from fastapi import APIRouter, Depends, status

from src.exchange_rate import exceptions
from src.exchange_rate import schemas
from src.exchange_rate.service import (
    get_exc_rate_list,
    get_exc_rate,
    add_exc_rate,
    upd_exc_rate,
)

router = APIRouter()


@router.get("/exchangeRates/", response_model=list[schemas.ExchangeRate])
def get_exchange_rates():
    return get_exc_rate_list()


@router.get(
    "/exchangeRate/", response_model=schemas.ExchangeRate, include_in_schema=False
)
def get_exchange_rate_empty_code():
    raise exceptions.NoExcRateCodeError()


@router.get("/exchangeRate/{code}", response_model=schemas.ExchangeRate)
def get_exchange_rate_by_code(code: str):
    exc_rate = get_exc_rate(code)
    if not exc_rate:
        raise exceptions.ExcRateNotFound()
    return exc_rate


@router.post(
    "/exchangeRates/",
    response_model=schemas.ExchangeRate,
    status_code=status.HTTP_201_CREATED,
)
def create_exchange_rate(
    exchange_rate_data: schemas.ExchangeRateCreate = Depends(
        schemas.ExchangeRateCreate.as_form
    ),
):
    return add_exc_rate(exchange_rate_data)


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
):
    return upd_exc_rate(code, exchange_rate_data)
