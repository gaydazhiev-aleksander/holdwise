from django.db import models


class AssetType(models.TextChoices):
    STOCK = 'stock', 'Stock'
    ETF = 'etf', 'ETF'
    CRYPTO = 'crypto', 'Crypto'
    OTHER = 'other', 'Other'