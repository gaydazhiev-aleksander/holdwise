from django.db.models import Q
from django.views.generic import DetailView, ListView

import assets
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
