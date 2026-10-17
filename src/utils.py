from decimal import ROUND_HALF_UP, Decimal

from .constants import AMOUNT_ACCURACY, EXCH_RATE_ACCURACY


def parse_currency_pair(pair: str) -> tuple[str, str]:
    return pair[:3], pair[3:]


def round_decimal(n: Decimal, decimals: int) -> Decimal:
    return n.quantize(Decimal(1).scaleb(-decimals), rounding=ROUND_HALF_UP)


def round_rate(rate: Decimal) -> Decimal:
    return round_decimal(rate, EXCH_RATE_ACCURACY)


def round_amount(amount: Decimal) -> Decimal:
    return round_decimal(amount, AMOUNT_ACCURACY)
