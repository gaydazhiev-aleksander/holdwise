from decimal import Decimal

from django import forms

from assets.forms import TickerLookupForm
from .choices import MovementType
from .models import CashMovement, Holding, Portfolio


class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ['name', 'description', 'strategy']
        labels = {
            'name': 'Portfolio Name',
            'strategy': 'Investment Strategy',
        }
        help_texts = {
            'name': 'Short name, eg. Long-term, Crypto',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'eg. Long-term',
                'class': 'form-control',
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'What is this portfolio for(optional)',
                'class': 'form-control',
            }),
            'strategy': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_name(self):
        name = self.cleaned_data['name'].strip()

        if Portfolio.objects.filter(name__iexact=name).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This portfolio already exists!")

        return name


class AddHoldingForm(TickerLookupForm):
    MAX_SHARES = Decimal('999999999999')

    shares = forms.DecimalField(
        max_digits=18,
        decimal_places=6,
        min_value=Decimal('0.000001'),
        label='Number of shares',
        error_messages={'min_value': 'Shares must be greater than 0.'},
        widget=forms.NumberInput(attrs={
            'placeholder': '10',
            'step': 'any',
            'class': 'form-control',
        })
    )
    price = forms.DecimalField(
        max_digits=14,
        decimal_places=4,
        min_value=Decimal('0.0001'),
        label='Buy price',
        help_text='Price of 1 share',
        error_messages={'min_value': 'Price must be greater than 0.'},
        widget=forms.NumberInput(attrs={
            'placeholder': '150.00',
            'step': 'any',
            'class': 'form-control',
        })
    )
    pay_from_cash = forms.BooleanField(
        required=False,
        label='Pay from cash reserve',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )

    def __init__(self, *args, portfolio, **kwargs):
        super().__init__(*args, **kwargs)
        self.portfolio = portfolio
        self.fields['pay_from_cash'].help_text = f'Available cash: {portfolio.cash_balance:,.2f}'

    def clean(self):
        cleaned_data = super().clean()
        shares = cleaned_data.get('shares')
        price = cleaned_data.get('price')
        pay_from_cash = cleaned_data.get('pay_from_cash')

        if pay_from_cash and shares and price:
            cost = shares * price
            balance = self.portfolio.cash_balance
            if cost > balance:
                self.add_error(
                    'pay_from_cash',
                    f'Not enough cash: thsi costs {cost:,.2f}, but you have {balance:,.2f}',
                )

        if self.asset and shares:
            existing = Holding.objects.filter(portfolio=self.portfolio, asset=self.asset).first()
            if existing is not None and existing.shares + shares > self.MAX_SHARES:
                self.add_error(
                    'shares',
                    f'You already hold {existing.shares.normalize():f} shares of {self.asset.ticker} '
                    f'The total cannot exceed {self.MAX_SHARES:,}',
                )

        return cleaned_data


class HoldingForm(forms.ModelForm):
    class Meta:
        model = Holding
        fields = ['asset', 'shares', 'average_buy_price']
        labels = {
            'asset': 'Asset',
            'shares': 'Number of shares',
            'average_buy_price': 'Average buy price',
        }
        help_texts = {
            'average_buy_price': 'Price per share, editting this does not change your cash',
        }
        widgets = {
            'asset': forms.Select(attrs={'class': 'form-select'}),
            'shares': forms.NumberInput(attrs={
                'step': 'any',
                'class': 'form-control',
            }),
            'average_buy_price': forms.NumberInput(attrs={
                'step': 'any',
                'class': 'form-control',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['asset'].disabled = True
        self.fields['asset'].help_text = ('The asset cant be changed, delete this holding and add a new one instead')


class SellHoldingForm(forms.Form):
    MAX_PROCEEDS = Decimal('999999999999.99')

    shares = forms.DecimalField(
        max_digits=18,
        decimal_places=6,
        min_value=Decimal('0.000001'),
        label='Shares to sell',
        error_messages={'min_value': 'Shares must be greater than 0.'},
        widget=forms.NumberInput(attrs={
            'step': 'any',
            'class': 'form-control',
        }),
    )
    price = forms.DecimalField(
        max_digits=14,
        decimal_places=4,
        min_value=Decimal('0.0001'),
        label='Sell price per share',
        help_text='Pre-filled with the latest market price',
        error_messages={'min_value': 'Price must be greater than 0.'},
        widget=forms.NumberInput(attrs={
            'step': 'any',
            'class': 'form-control',
        }),
    )

    def __init__(self, *args, holding, **kwargs):
        super().__init__(*args, **kwargs)
        self.holding = holding
        self.fields['shares'].help_text = f'You hold {holding.shares.normalize():f} shares'

    def clean_shares(self):
        shares = self.cleaned_data['shares']

        if shares > self.holding.shares:
            raise forms.ValidationError(
                f'You only hold {self.holding.shares.normalize():f} shares of {self.holding.asset.ticker}'
            )

        return shares

    def clean(self):
        cleaned_data = super().clean()
        shares = cleaned_data.get('shares')
        price = cleaned_data.get('price')

        if shares and price and shares * price > self.MAX_PROCEEDS:
            self.add_error('price', 'The sale amount is too large to record')

        return cleaned_data


class CashMovementForm(forms.ModelForm):
    class Meta:
        model = CashMovement
        fields = ['movement_type', 'amount', 'note']
        labels = {
            'movement_type': 'Type',
            'amount': 'Amount',
            'note': 'Note',
        }
        help_texts = {
            'note': 'Optional, eg. "Monthly savings"',
        }
        widgets = {
            'movement_type': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'amount': forms.NumberInput(attrs={
                'step': '0.01',
                'placeholder': '500.00',
                'class': 'form-control',
            }),
            'note': forms.TextInput(attrs={
                'placeholder': 'Optional',
                'class': 'form-control',
            }),
        }

    def __init__(self, *args, portfolio, **kwargs):
        super().__init__(*args, **kwargs)
        self.portfolio = portfolio
        self.fields['movement_type'].choices = [
            (MovementType.DEPOSIT, MovementType.DEPOSIT.label),
            (MovementType.WITHDRAWAL, MovementType.WITHDRAWAL.label),
        ]
        self.fields['amount'].help_text = f'Available cash: {portfolio.cash_balance:,.2f}'

    def clean(self):
        cleaned_data = super().clean()
        movement_type = cleaned_data.get('movement_type')
        amount = cleaned_data.get('amount')

        if movement_type == MovementType.WITHDRAWAL and amount:
            balance = self.portfolio.cash_balance
            if amount > balance:
                self.add_error('amount', f'You can only withdraw up to {balance:,.2f}.')

        return cleaned_data