from django.db import models
from django.utils import timezone

from .services import MarketDataService


class AssetManager(models.Manager):
    def get_or_fetch(self, ticker, service=None):
        ticker = ticker.strip().upper()

        try:
            return self.get(ticker=ticker)
        except self.model.DoesNotExist:
            pass

        service = service or MarketDataService()
        details = service.fetch_asset_details(ticker)
        return self.create(
            ticker=ticker,
            price_updated_at=timezone.now(),
            **details,
        )
