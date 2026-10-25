from django.core.validators import MinLengthValidator
from django.db import models


class Watchlist(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        validators=[MinLengthValidator(2)],
        error_messages={
            'unique': 'A watchlist with this name already exists.',
        },
    )
    notes = models.TextField(blank=True)
    assets = models.ManyToManyField(
        'assets.Asset',
        related_name='watchlists',
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def assets_count(self):
        """Number of assets in this watchlist"""
        return self.assets.count()
