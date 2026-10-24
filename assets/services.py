from decimal import Decimal

import yfinance as yf

from .choices import AssetType
from .exceptions import MarketDataUnavailableError, TickerNotFoundError


class MarketDataService:
    """Fetches asset details and prices from Yahoo Finance."""

    QUOTE_TYPE_MAP = {
        'EQUITY': AssetType.STOCK,
        'ETF': AssetType.ETF,
        'CRYPTOCURRENCY': AssetType.CRYPTO,
    }

    UNAVAILABLE_MESSAGE = 'Market data is temporarily unavailable. Please try again later.'

    @staticmethod
    def _to_decimal(value):
        return Decimal(str(value)).quantize(Decimal('0.0001'))

    @staticmethod
    def _not_found_error(ticker):
        return TickerNotFoundError(f'No asset found with ticker "{ticker}".')

    @classmethod
    def _map_asset_type(cls, quote_type):
        return cls.QUOTE_TYPE_MAP.get(quote_type, AssetType.OTHER)

    def fetch_price(self, ticker):
        """Return the latest price for the ticker as a Decimal."""
        try:
            price = yf.Ticker(ticker).fast_info['lastPrice']
        except KeyError as error:
            raise self._not_found_error(ticker) from error
        except Exception as error:
            raise MarketDataUnavailableError(self.UNAVAILABLE_MESSAGE) from error

        if price is None:
            raise self._not_found_error(ticker)

        return self._to_decimal(price)

    def fetch_asset_details(self, ticker):
        """Return a dict with the asset's name, type, sector, currency and current price."""
        try:
            info = yf.Ticker(ticker).info
        except Exception as error:
            raise MarketDataUnavailableError(self.UNAVAILABLE_MESSAGE) from error

        if not info.get('quoteType'):
            raise self._not_found_error(ticker)

        return {
            'name': info.get('longName') or info.get('shortName') or ticker,
            'asset_type': self._map_asset_type(info.get('quoteType')),
            'sector': info.get('sector') or '',
            'currency': info.get('currency') or 'USD',
            'last_price': self.fetch_price(ticker),
        }
