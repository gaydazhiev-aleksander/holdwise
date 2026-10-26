import re
from decimal import Decimal

from django import forms

from assets.exceptions import MarketDataError
from assets.models import Asset

from .models import Holding, Portfolio


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


class AddHoldingForm(forms.Form):
    ticker = forms.CharField(
        max_length=10,
        label='Ticker symbol',
        help_text='eg. AAPL, SPY, BTC-USD',
        widget=forms.TextInput(attrs={
            'placeholder': 'AAPL',
            'class': 'form-control',
        })
    )
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
        self.asset = None
        self.fields['pay_from_cash'].help_text = f'Available cash: {portfolio.cash_balance:,.2f}'

    def clean_ticker(self):
        ticker = self.cleaned_data['ticker'].strip().upper()

        if not re.fullmatch(r'[A-Z0-9.\-]+', ticker):
            raise forms.ValidationError("Invalid ticker")

        try:
            self.asset = Asset.objects.get_or_fetch(ticker)
        except MarketDataError as error:
            raise forms.ValidationError(str(error)) from error

        return ticker

    def clean(self):
        cleaned_data = super().clean()
        shares = self.cleaned_data.get('shares')
        price = self.cleaned_data.get('price')
        pay_from_cash = self.cleaned_data.get('pay_from_cash')

        if pay_from_cash and shares and price:
            cost = shares * price
            balance = self.portfolio.cash_balance
            if cost > balance:
                self.add_error(
                    'pay_from_cash',
                    f'Not enough cash: this costs {cost:,.2f}, but you have {balance:,.2f}'
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