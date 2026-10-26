from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


def _to_decimal(value):
    if value is None or value == '':
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None


@register.filter
def money(value, symbol='$'):
    amount = _to_decimal(value)
    if amount is None:
        return '—'
    sign = '-' if amount < 0 else ''
    return f'{sign}{symbol}{abs(amount):,.2f}'


@register.filter
def shares(value):
    amount = _to_decimal(value)
    if amount is None:
        return '—'
    return f'{amount.normalize():f}'


@register.filter
def signed_percent(value):
    amount = _to_decimal(value)
    if amount is None:
        return '—'
    return f'{amount:+.2f}%'


@register.filter
def pl_class(value):
    amount = _to_decimal(value)
    if amount is None:
        return 'text-secondary'
    return 'text-profit' if amount >= 0 else 'text-loss'


@register.inclusion_tag('partials/profit_loss.html')
def profit_loss(amount, percent=None):
    return {'amount': amount, 'percent': percent}