from src.exceptions import BadRequest, NotFound


class NoExcRateCodeError(BadRequest):
    DETAIL = "Exchange rate code is required"


class ExcRateNotFound(NotFound):
    DETAIL = "Exchange rate not found"


class CurrencyPairExcRateNotFound(NotFound):
    DETAIL = "Exchange rate for currency pair not found"
