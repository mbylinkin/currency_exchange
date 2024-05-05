from decimal import Decimal
from typing import Self
from fastapi import Form
from pydantic import AliasChoices, BaseModel, Field, field_serializer
from src.currency.schemas import Currency


class ExchangeRateBase(BaseModel):
    rate: Decimal = Field(
        ..., description="Currency rate", ge=0.000001, decimal_places=6
    )

    @field_serializer("rate", when_used="json")
    def serialize_rate(rate: Decimal) -> float:
        return float(rate)


class ExchangeRateCreate(ExchangeRateBase):
    base_currency_code: str
    target_currency_code: str

    @classmethod
    def as_form(
        cls,
        baseCurrencyCode: str = Form(...),
        targetCurrencyCode: str = Form(...),
        rate: Decimal = Form(..., alias="rate"),
    ) -> Self:
        return cls(
            base_currency_code=baseCurrencyCode,
            target_currency_code=targetCurrencyCode,
            rate=rate,
        )


class ExchangeRate(ExchangeRateBase):
    id: int
    base_currency: Currency = Field(
        ...,
        alias="baseCurrency",
        validation_alias=AliasChoices("base_currency", "baseCurrency"),
    )
    target_currency: Currency = Field(
        ...,
        alias="targetCurrency",
        validation_alias=AliasChoices("target_currency", "targetCurrency"),
    )

    class Config:
        from_attributes = True


class ExchangeRateUpdate(ExchangeRateBase):
    @classmethod
    def as_form(
        cls,
        rate: Decimal = Form(...),
    ) -> Self:
        return cls(rate=rate)
