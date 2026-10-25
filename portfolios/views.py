from django.views.generic import DetailView, ListView

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