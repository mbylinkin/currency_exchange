from fastapi import APIRouter, Depends, status

from src.currency import exceptions, schemas
from src.currency.service import (
    get_currency_list,
    add_currency,
    get_valid_currency,
)

router = APIRouter()


@router.get("/currencies/", response_model=list[schemas.Currency])
def get_currencies():
    return get_currency_list()


@router.get("/currency/", response_model=schemas.Currency, include_in_schema=False)
def get_currency_empty_code():
    raise exceptions.NoCurrencyCodeError()


@router.get("/currency/{code}", response_model=schemas.Currency)
def get_currency_by_code(code: str):
    return get_valid_currency(code)


@router.post(
    "/currencies/",
    response_model=schemas.Currency,
    status_code=status.HTTP_201_CREATED,
)
def create_currency(
    currency_data: schemas.CurrencyCreate = Depends(schemas.CurrencyCreate.as_form),
):
    try:
        return add_currency(currency_data)
    except exceptions.AlreadyExists:
        raise exceptions.CurrencyAlreadyExists()
