from decimal import Decimal

from django.views.generic import TemplateView

from assets.models import Asset
from portfolios.models import CashMovement, Portfolio
from watchlists.models import Watchlist


class HomeView(TemplateView):
    template_name = 'common/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        portfolios = list(Portfolio.objects.prefetch_related('holdings__asset', 'cash_movements'))
        totals = Asset.objects.position_totals()
        cash_total = sum((portfolio.cash_balance for portfolio in portfolios), Decimal('0'))

        context['portfolios'] = portfolios
        context['totals'] = totals
        context['cash_total'] = cash_total
        context['net_worth'] = totals['market_value'] + cash_total
        context['recent_movements'] = CashMovement.objects.select_related('portfolio')[:5]
        context['watchlist_count'] = Watchlist.objects.count()
        return context


class AboutView(TemplateView):
    template_name = 'common/about.html'