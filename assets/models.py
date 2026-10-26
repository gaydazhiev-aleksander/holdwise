from datetime import timedelta
from decimal import Decimal

from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone

from .choices import AssetType
from .exceptions import MarketDataError
from .managers import AssetManager
from .services import MarketDataService


class Asset(models.Model):
    PRICE_MAX_AGE = timedelta(minutes=1)

    ticker = models.CharField(
        max_length=10,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Z0-9.\-]+$',
                message='Ticker can only contain capital letters, digits, dots and dashes.',
            ),
        ],
        error_messages={
            'unique': 'This ticker is already in the system.',
        },
    )
    name = models.CharField(max_length=150)
    asset_type = models.CharField(
        max_length=10,
        choices=AssetType.choices,
        default=AssetType.STOCK,
    )
    sector = models.CharField(max_length=100, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    last_price = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
    )
    price_updated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = AssetManager()

    class Meta:
        ordering = ['ticker']

    def __str__(self):
        return f'{self.ticker} - {self.name}'

    @property
    def is_price_stale(self):
        """true if the price was never fetched or is older than PRICE_MAX_AGE"""
        return (
                self.price_updated_at is None
                or timezone.now() - self.price_updated_at > self.PRICE_MAX_AGE
        )

    def refresh_price(self, service=None):
        """Fetch a fresh price if the current one is stale.
        return True if the price is up to date afterwards, False if fetching failed"""
        if not self.is_price_stale:
            return True

        service = service or MarketDataService()

        try:
            self.last_price = service.fetch_price(self.ticker)
        except MarketDataError:
            return False

        self.price_updated_at = timezone.now()
        self.save(update_fields=['last_price', 'price_updated_at'])
        return True
