from fastapi import APIRouter
from fastapi.params import Query

from src.exchange import schemas
from src.exchange.service import exc_currency


router = APIRouter()


@router.get("/exchange/", response_model=schemas.Exchange)
def exchange_currency(
    from_currency: str = Query(..., alias="from"),
    to_currency: str = Query(..., alias="to"),
    amount: float = Query(...),
):
    return exc_currency(from_currency, to_currency, amount)
