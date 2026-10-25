from decimal import Decimal

from django.core.validators import MinLengthValidator, MinValueValidator
from django.db import models
from django.urls import reverse

from .choices import MovementType, Strategy


class Portfolio(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        validators=[MinLengthValidator(2)],
        error_messages={
            'unique': 'A portfolio with this name already exists.',
        },
    )
    description = models.TextField(blank=True)
    strategy = models.CharField(
        max_length=20,
        choices=Strategy.choices,
        default=Strategy.BALANCED,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('portfolios:detail', kwargs={'pk': self.pk})

    @property
    def cash_balance(self):
        """Sum of all cash movements, positive in and negative out."""
        return sum(
            (movement.signed_amount for movement in self.cash_movements.all()),
            Decimal('0'),
        )

    @property
    def holdings_value(self):
        """Current value of all holdings, skipping those without a price."""
        values = [holding.current_value for holding in self.holdings.all()]
        return sum((value for value in values if value is not None), Decimal('0'))

    @property
    def total_profit_loss(self):
        """Total profit or loss across holdings, skipping those without a price."""
        values = [holding.profit_loss for holding in self.holdings.all()]
        return sum((value for value in values if value is not None), Decimal('0'))

    @property
    def total_value(self):
        """Holdings value plus cash balance."""
        return self.holdings_value + self.cash_balance


class Holding(models.Model):
    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name='holdings',
    )
    asset = models.ForeignKey(
        'assets.Asset',
        on_delete=models.PROTECT,
        related_name='holdings',
    )
    shares = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        validators=[
            MinValueValidator(Decimal('0.000001'), message='Shares must be greater than zero.'),
        ],
    )
    average_buy_price = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        validators=[
            MinValueValidator(Decimal('0.0001'), message='Price must be greater than zero.'),
        ],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['asset__ticker']
        constraints = [
            models.UniqueConstraint(
                fields=['portfolio', 'asset'],
                name='unique_asset_per_portfolio',
            ),
        ]

    def __str__(self):
        return f'{self.shares} {self.asset.ticker} in {self.portfolio}'

    @property
    def cost_basis(self):
        """Total money put in: shares times the average buy price."""
        return self.shares * self.average_buy_price

    @property
    def current_value(self):
        """Shares times the latest price, or None if there is no price."""
        price = self.asset.last_price
        if price is None:
            return None
        return self.shares * price

    @property
    def profit_loss(self):
        """Current value minus cost basis, or None if there is no price."""
        current_value = self.current_value
        if current_value is None:
            return None
        return current_value - self.cost_basis

    @property
    def profit_loss_percent(self):
        """Profit or loss as a percentage of cost basis, or None if there is no price."""
        profit_loss = self.profit_loss
        if profit_loss is None:
            return None
        return profit_loss / self.cost_basis * Decimal('100')


class CashMovement(models.Model):
    INFLOW_TYPES = (MovementType.DEPOSIT, MovementType.SALE)

    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name='cash_movements',
    )
    movement_type = models.CharField(
        max_length=20,
        choices=MovementType.choices,
    )
    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal('0.01'), message='Amount must be at least 0.01.'),
        ],
    )
    note = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_movement_type_display()} of {self.amount} ({self.portfolio})'

    @property
    def signed_amount(self):
        """Positive for money coming in, negative for money going out."""
        if self.movement_type in self.INFLOW_TYPES:
            return self.amount
        return -self.amount
