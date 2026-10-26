from django.db import models
from django.utils import timezone

from .services import MarketDataService


class AssetQuerySet(models.QuerySet):
    def owned(self):
        return self.filter(holdings__isnull=False).distinct()

    def refresh_prices(self):
        """Refresh old prices."""
        refreshed = already_fresh = failed = 0

        for asset in self:
            if not asset.is_price_stale:
                already_fresh += 1
                continue
            elif asset.refresh_price():
                refreshed += 1
            else:
                failed += 1

        return refreshed, already_fresh, failed



class AssetManager(models.Manager.from_queryset(AssetQuerySet)):
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
