from django.shortcuts import render
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, DetailView, ListView, UpdateView, DeleteView

from .forms import WatchlistForm
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