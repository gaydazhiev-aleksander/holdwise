from django import forms

from assets.forms import TickerLookupForm

from .models import Watchlist


class WatchlistForm(forms.ModelForm):
    class Meta:
        model = Watchlist
        fields = ['name', 'notes']
        labels = {
            'name': 'Watchlist Name',
        }
        help_texts = {
            'name': 'eg. "Tech to buy" or "Dividend ideas"',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': ' e.g. Tech to buy',
                'class': 'form-control',
            }),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Why are you watching these? (optional)',
                'class': 'form-control',
            }),
        }

    def clean_name(self):
        name = self.cleaned_data['name'].strip()

        if Watchlist.objects.filter(name__iexact=name).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Watchlist already exists')

        return name


class AddToWatchlistForm(TickerLookupForm):
    def __init__(self, *args, watchlist, **kwargs):
        super().__init__(*args, **kwargs)
        self.watchlist = watchlist

    def clean_ticker(self):
        ticker = super().clean_ticker()

        if self.watchlist.assets.filter(pk=self.asset.pk).exists():
            raise forms.ValidationError(f'{ticker} is already on the watchlist')

        return ticker