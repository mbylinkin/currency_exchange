from decimal import Decimal
from pydantic import AliasChoices, BaseModel, Field, field_serializer
from src.currency.schemas import Currency


class Exchange(BaseModel):
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

    rate: Decimal = Field(
        ..., description="Currency rate", ge=0.000001, decimal_places=6
    )
    amount: Decimal = Field(..., description="Amount", ge=0.01, decimal_places=2)
    converted_amount: Decimal = Field(
        ...,
        alias="convertedAmount",
        validation_alias=AliasChoices("converted_amount", "convertedAmount"),
        ge=0.01,
        decimal_places=2,
    )

    @field_serializer("rate", when_used="json")
    def serialize_rate(rate: Decimal) -> float:
        return float(rate)

    @field_serializer("amount", when_used="json")
    def serialize_amount(amount: Decimal) -> float:
        return float(amount)

    @field_serializer("converted_amount", when_used="json")
    def serialize_converted_amount(converted_amount: Decimal) -> float:
        return float(converted_amount)
