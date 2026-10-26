from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, FormView, ListView, UpdateView, View

from .forms import AddToWatchlistForm, WatchlistForm
from .models import Watchlist


class WatchlistListView(ListView):
    queryset = Watchlist.objects.prefetch_related('assets')
    template_name = 'watchlists/watchlist_list.html'
    context_object_name = 'watchlists'


class WatchlistDetailView(DetailView):
    queryset = Watchlist.objects.prefetch_related('assets')
    template_name = 'watchlists/watchlist_detail.html'
    context_object_name = 'watchlist'


class WatchlistCreateView(SuccessMessageMixin, CreateView):
    model = Watchlist
    form_class = WatchlistForm
    template_name = 'watchlists/watchlist_form.html'
    success_message = 'Watchlist "%(name)s" created successfully.'


class WatchlistUpdateView(SuccessMessageMixin, UpdateView):
    model = Watchlist
    form_class = WatchlistForm
    template_name = 'watchlists/watchlist_form.html'
    success_message = 'Watchlist "%(name)s" updated successfully.'


class WatchlistDeleteView(SuccessMessageMixin, DeleteView):
    model = Watchlist
    template_name = 'watchlists/watchlist_confirm_delete.html'
    context_object_name = 'watchlist'
    success_url = reverse_lazy('watchlists:list')

    def get_success_message(self, cleaned_data):
        return f'Watchlist "{self.object.name}" was deleted successfully.'


class WatchlistAddAssetView(FormView):
    form_class = AddToWatchlistForm
    template_name = 'watchlists/watchlist_add_asset.html'

    def dispatch(self, request, *args, **kwargs):
        self.watchlist = get_object_or_404(Watchlist, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['watchlist'] = self.watchlist
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['watchlist'] = self.watchlist
        return context

    def form_valid(self, form):
        self.watchlist.assets.add(form.asset)
        messages.success(self.request, f'{form.asset.ticker} was added to {self.watchlist.name}')
        return redirect(self.watchlist)


class WatchlistRemoveAssetView(View):
    http_method_names = ['post']

    def post(self, request, pk, asset_pk):
        watchlist = get_object_or_404(Watchlist, pk=pk)
        asset = get_object_or_404(watchlist.assets, pk=asset_pk)
        watchlist.assets.remove(asset)
        messages.success(request, f'{asset.ticker} was removed from {watchlist.name}')
        return redirect(watchlist)