from src.exceptions import AlreadyExists, BadRequest, NotFound


class NoCurrencyCodeError(BadRequest):
    DETAIL = "Currency code is required"


class CurrencyNotFound(NotFound):
    DETAIL = "Currency not found"


class CurrencyAlreadyExists(AlreadyExists):
    DETAIL = "Currency with this code already exists"
