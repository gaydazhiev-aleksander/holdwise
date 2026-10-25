from django import forms

from .choices import AssetType


class AssetFilterForm(forms.Form):
    SORT_CHOICES = [
        ('ticker', 'Ticker (A-Z)'),
        ('name', 'Name (A-Z)'),
        ('-last_price', 'Price (high to low)'),
        ('last_price', 'Price (low to high)'),
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
