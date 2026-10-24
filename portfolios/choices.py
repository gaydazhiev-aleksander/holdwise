from django.db import models


class Strategy(models.TextChoices):
    GROWTH = 'growth', 'Growth'
    DIVIDEND = 'dividend', 'Dividend'
    VALUE = 'value', 'Value'
    SPECULATIVE = 'speculative', 'Speculative'
    BALANCED = 'balanced', 'Balanced'


class MovementType(models.TextChoices):
    DEPOSIT = 'deposit', 'Deposit'
    WITHDRAWAL = 'withdrawal', 'Withdrawal'
    SALE = 'sale', 'Sale proceeds'
    PURCHASE = 'purchase', 'Purchase'
