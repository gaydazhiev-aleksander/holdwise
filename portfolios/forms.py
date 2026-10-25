from django import forms

from .models import Portfolio


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
