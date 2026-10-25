from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import PortfolioForm
from .models import Portfolio


class PortfolioListView(ListView):
    queryset = Portfolio.objects.prefetch_related('holdings__asset', 'cash_movements')
    template_name = 'portfolios/portfolio_list.html'
    context_object_name = 'portfolios'


class PortfolioDetailView(DetailView):
    queryset = Portfolio.objects.prefetch_related('holdings__asset', 'cash_movements')
    template_name = 'portfolios/portfolio_detail.html'
    context_object_name = 'portfolio'

    def get_object(self, queryset=None):
        portfolio = super().get_object(queryset)
        for holding in portfolio.holdings.all():
            holding.asset.refresh_price()
        return portfolio


class PortfolioCreateView(SuccessMessageMixin, CreateView):
    model = Portfolio
    form_class = PortfolioForm
    template_name = 'portfolios/portfolio_form.html'
    success_message = 'Portfolio "%(name)s" was created.'


class PortfolioUpdateView(SuccessMessageMixin, UpdateView):
    model = Portfolio
    form_class = PortfolioForm
    template_name = 'portfolios/portfolio_form.html'
    success_message = 'Portfolio "%(name)s" was updated.'