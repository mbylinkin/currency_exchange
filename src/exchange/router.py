from decimal import Decimal

from fastapi import APIRouter
from fastapi.params import Query

from src.exchange import schemas
from src.exchange.service import exc_currency

router = APIRouter()


@router.get("/exchange", response_model=schemas.Exchange)
def exchange_currency(
    from_currency: str = Query(..., alias="from"),
    to_currency: str = Query(..., alias="to"),
    # Decimal rejects inf/NaN; float accepts inf even with allow_inf_nan=False
    amount: Decimal = Query(..., gt=0),
):
    return exc_currency(from_currency, to_currency, amount)
