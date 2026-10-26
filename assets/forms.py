import re

from django import forms

from .choices import AssetType
from .exceptions import MarketDataError
from .models import Asset


class AssetFilterForm(forms.Form):
    SORT_CHOICES = [
        ('-market_value', 'Value (high to low)'),
        ('-profit_loss_percent', 'P/L % (best first)'),
        ('profit_loss_percent', 'P/L % (worst first)'),
        ('ticker', 'Ticker (A-Z)'),
        ('name', 'Name (A-Z)'),
    ]

    q = forms.CharField(
        required=False,
        max_length=50,
        label='Search',
        widget=forms.TextInput(attrs={
            'placeholder': 'Ticker or name',
            'class': 'form-control',
        }),
    )
    asset_type = forms.ChoiceField(
        required=False,
        label='Type',
        choices=[('', 'All types')] + AssetType.choices,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    sort = forms.ChoiceField(
        required=False,
        label='Sort by',
        choices=SORT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )


class TickerLookupForm(forms.Form):
    ticker = forms.CharField(
        max_length=10,
        label='Ticker symbol',
        help_text='eg. AAPL, BTC-USD, SPY',
        widget=forms.TextInput(attrs={
            'placeholder': 'AAPL',
            'class': 'form-control',
        }),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.asset = None

    def clean_ticker(self):
        ticker = self.cleaned_data['ticker'].strip().upper()

        if not re.fullmatch(r'[A-Z0-9.\-]+', ticker):
            raise forms.ValidationError('Ticker can only contain letters, digits, dots and dashes.')

        try:
            self.asset = Asset.objects.get_or_fetch(ticker)
        except MarketDataError as error:
            raise forms.ValidationError(str(error)) from error

        return ticker
