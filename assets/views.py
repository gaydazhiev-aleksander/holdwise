from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import DetailView, ListView, View

from .forms import AssetFilterForm
from .models import Asset


class AssetListView(ListView):
    model = Asset
    template_name = 'assets/asset_list.html'
    context_object_name = 'assets'
    paginate_by = 10

    def get_queryset(self):
        self.form = AssetFilterForm(self.request.GET or None)
        queryset = Asset.objects.with_positions()
        sort = '-market_value'

        if self.form is not None and self.form.is_valid():
            q = self.form.cleaned_data.get('q')
            asset_type = self.form.cleaned_data.get('asset_type')
            sort = self.form.cleaned_data.get('sort') or sort

            if q:
                queryset = queryset.filter(Q(ticker__icontains=q) | Q(name__icontains=q))
            if asset_type:
                queryset = queryset.filter(asset_type=asset_type)

        return queryset.order_by(sort)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form or AssetFilterForm()
        context['totals'] = Asset.objects.position_totals()
        return context

class AssetDetailView(DetailView):
    model = Asset
    template_name = 'assets/asset_detail.html'
    context_object_name = 'asset'
    slug_field = 'ticker'
    slug_url_kwarg = 'ticker'

    def get_object(self, queryset=None):
        asset = super().get_object(queryset)
        asset.refresh_price()
        return asset


class RefreshPricesView(View):
    http_method_names = ['post']

    def post(self, request):
        assets = Asset.objects.owned()
        portfolio_id = request.POST.get('portfolio')
        if portfolio_id:
            assets = assets.filter(holdings__portfolio_id=portfolio_id)

        refreshed, already_refreshed, failed = assets.refresh_prices()

        if failed:
            messages.warning(
                request,
                f'Updated {refreshed} price(s). {failed} could not be refreshed. '
                f'Yahoo Finance may be unavailable.',
            )
        elif refreshed:
            messages.success(request, f'Updated {refreshed} price(s).')
        else:
            messages.info(request, f'All prices are already refreshed.')

        next_url = request.POST.get('next')
        if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
            next_url = reverse('assets:list')

        return redirect(next_url)