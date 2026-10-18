from collections.abc import Iterable
from typing import NoReturn

from fastapi import APIRouter, Depends, status

from src import models
from src.currency import exceptions, schemas
from src.currency.service import (
    add_currency,
    get_currency_list,
    get_valid_currency,
)
from src.exceptions import AlreadyExists

router = APIRouter()


@router.get("/currencies", response_model=list[schemas.Currency])
def get_currencies() -> Iterable[models.Currency]:
    return get_currency_list()


@router.get("/currency/", response_model=schemas.Currency, include_in_schema=False)
def get_currency_empty_code() -> NoReturn:
    raise exceptions.NoCurrencyCodeError()


@router.get("/currency/{code}", response_model=schemas.Currency)
def get_currency_by_code(code: str) -> models.Currency:
    return get_valid_currency(code)


@router.post(
    "/currencies",
    response_model=schemas.Currency,
    status_code=status.HTTP_201_CREATED,
)
def create_currency(
    currency_data: schemas.CurrencyCreate = Depends(schemas.CurrencyCreate.as_form),
) -> models.Currency:
    try:
        return add_currency(currency_data)
    except AlreadyExists:
        raise exceptions.CurrencyAlreadyExists()
