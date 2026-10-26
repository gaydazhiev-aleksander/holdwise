from dataclasses import dataclass
from decimal import Decimal

from django.db import transaction
from django.db.models import Model

from .choices import MovementType
from .models import CashMovement, Holding


@dataclass
class SaleResults:
    proceeds: Decimal
    profit_loss: Decimal
    position_closed: bool


class HoldingService:
    MONEY_PLACES = Decimal('0.01')
    PRICE_PLACES = Decimal('0.0001')

    @classmethod
    def _to_money(cls, value):
        return value.quantize(cls.MONEY_PLACES)

    def buy(self, portfolio, asset, shares, price, pay_from_cash=False):
        """adds shares to a portfolio, merging with an existing holding if there is one
        if pay_from_cash is True, the cost is recorded as a purchase cash movement"""
        with transaction.atomic():
            holding = Holding.objects.filter(portfolio=portfolio, asset=asset).first()

            if holding is None:
                holding = Holding.objects.create(
                    portfolio=portfolio,
                    asset=asset,
                    shares=shares,
                    average_buy_price=price,
                )
            else:
                total_cost = holding.shares * holding.average_buy_price + shares * price
                holding.shares += shares
                holding.average_buy_price = (total_cost / holding.shares).quantize(self.PRICE_PLACES)
                holding.save()

            if pay_from_cash:
                CashMovement.objects.create(
                    portfolio=portfolio,
                    movement_type=MovementType.PURCHASE,
                    amount=self._to_money(shares * price),
                    note=f'Bought {shares} {asset.ticker} at {price}'
                )

        return holding

    def sell(self, holding, shares, price):
        """sell shares from a holding and record the proceeds as cash
        Deleates the holding if all shares are sold, returns a SaleResult"""
        if shares > holding.shares:
            raise ValueError('Cannot sell more shares than are held')

        proceeds = self._to_money(shares * price)
        profit_loss = self._to_money((price - holding.average_buy_price) * shares)

        with transaction.atomic():
            holding.shares -= shares
            position_closed = holding.shares == 0

            if position_closed:
                holding.delete()
            else:
                holding.save()

            CashMovement.objects.create(
                portfolio=holding.portfolio,
                movement_type=MovementType.SALE,
                amount=proceeds,
                note=f'Sold {shares} {holding.asset.ticker} at {price}',
            )

        return SaleResults(
            proceeds=proceeds,
            profit_loss=profit_loss,
            position_closed=position_closed,
        )
