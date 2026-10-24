from decimal import Decimal

from django.db import models
from django.core.validators import RegexValidator, MinValueValidator


class AssetType(models.TextChoices):
    STOCK = 'stock', 'Stock'
    ETF = 'etf', 'ETF'
    CRYPTO = 'crypto', 'Crypto'
    OTHER = 'other', 'Other'


class Asset(models.Model):
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

    class Meta:
        ordering = ['ticker']

    def __str__(self):
        return f'{self.ticker} - {self.name}'
