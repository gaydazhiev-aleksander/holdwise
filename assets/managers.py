from decimal import Decimal

from django.db import models
from django.db.models import Count, DecimalField, ExpressionWrapper, F, Sum, Value
from django.utils import timezone

from .services import MarketDataService


class AssetQuerySet(models.QuerySet):
    def owned(self):
        return self.filter(holdings__isnull=False).distinct()

    def with_positions(self):
        money = DecimalField(max_digits=24, decimal_places=4)

        return (
            self.annotate(
                total_shares=Sum('holdings__shares'),
                total_cost=Sum(
                    F('holdings__average_buy_price') * F('holdings__shares'),
                    output_field=money,
                ),
                portfolio_count=Count('holdings'),
            )
            .filter(total_shares__gt=0)
            .annotate(
                average_cost=ExpressionWrapper(
                    F('total_cost') / F('total_shares'),
                    output_field=money,
                ),
                market_value=ExpressionWrapper(
                    F('total_shares') * F('last_price'),
                    output_field=money,
                ),
            )
            .annotate(
                profit_loss=ExpressionWrapper(
                    F('market_value') - F('total_cost'),
                    output_field=money,
                ),
            )
            .annotate(
                profit_loss_percent=ExpressionWrapper(
                    F('profit_loss') * Value(Decimal('100')) / F('total_cost'),
                    output_field=money,
                ),
            )
        )

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
