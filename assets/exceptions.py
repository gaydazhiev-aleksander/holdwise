class MarketDataError(Exception):
    """Something went wrong when trying to get market data"""


class TickerNotFoundError(MarketDataError):
    """The ticker doesn't exist on Yahoo."""


class MarketDataUnavailableError(MarketDataError):
    """Yahoo is unreachable or rate-limiting us."""