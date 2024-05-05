import math

from .constants import EXCH_RATE_ACCURACY


def parse_currency_pair(pair: str) -> tuple[str, str]:
    return pair[:3], pair[3:]


def round_up(n, decimals=EXCH_RATE_ACCURACY):
    multiplier = 10**decimals
    return math.ceil(n * multiplier) / multiplier
