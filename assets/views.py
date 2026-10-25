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
        queryset = super().get_queryset()

        if self.form is not None and self.form.is_valid():
            q = self.form.cleaned_data.get('q')
            asset_type = self.form.cleaned_data.get('asset_type')
            sort = self.form.cleaned_data.get('sort')

            if q:
                queryset = queryset.filter(Q(ticker__icontains=q) | Q(name__icontains=q))
            if asset_type:
                queryset = queryset.filter(asset_type=asset_type)
            if sort:
                queryset = queryset.order_by(sort)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form or AssetFilterForm()
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
