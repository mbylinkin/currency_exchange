from src.exceptions import NotFound


class CurrencyPairExcRateNotFound(NotFound):
    DETAIL = "Exchange rate for currency pair not found"
