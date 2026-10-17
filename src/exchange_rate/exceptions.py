from src.exceptions import AlreadyExists, BadRequest, NotFound


class NoExcRateCodeError(BadRequest):
    DETAIL = "Exchange rate code is required"


class ExcRateNotFound(NotFound):
    DETAIL = "Exchange rate not found"


class ExcRateAlreadyExists(AlreadyExists):
    DETAIL = "Exchange rate for this currency pair already exists"


class CurrencyPairExcRateNotFound(NotFound):
    DETAIL = "Exchange rate for currency pair not found"
