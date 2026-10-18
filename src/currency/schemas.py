import re
from typing import Self

from fastapi import Form
from pydantic import BaseModel, ConfigDict, field_validator


class CurrencyBase(BaseModel):
    name: str
    code: str
    sign: str


class CurrencyCreate(CurrencyBase):
    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        code: str = Form(...),
        sign: str = Form(...),
    ) -> Self:
        return cls(name=name, code=code, sign=sign)

    @field_validator("code")
    @classmethod
    def validate_currency_code(cls, v: str) -> str:
        # Length check (3 symbols)
        if len(v) != 3:
            raise ValueError("Currency code must be 3 characters long")

        # Check for letters only
        if not re.match(r"^[A-Za-z]+$", v):
            raise ValueError("Currency code must contain only letters (a-z or A-Z)")

        return v.upper()


class CurrencyUpdate(CurrencyBase):
    pass


class Currency(CurrencyBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
