from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, FormView, ListView, UpdateView

from .forms import AddHoldingForm, HoldingForm, PortfolioForm
from .models import Portfolio, Holding
from .services import HoldingService


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


class PortfolioDeleteView(SuccessMessageMixin, DeleteView):
    model = Portfolio
    template_name = 'portfolios/portfolio_confirm_delete.html'
    context_object_name = 'portfolio'
    success_url = reverse_lazy('portfolios:list')

    def get_success_message(self, cleaned_data):
        return f'Portfolio "{self.object.name}" was deleted'


class HoldingCreateView(FormView):
    form_class = AddHoldingForm
    template_name = 'portfolios/holding_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.portfolio = get_object_or_404(Portfolio, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['portfolio'] = self.portfolio
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['portfolio'] = self.portfolio
        return context

    def form_valid(self, form):
        holding = HoldingService().buy(
            self.portfolio,
            form.asset,
            form.cleaned_data['shares'],
            form.cleaned_data['price'],
            pay_from_cash=form.cleaned_data['pay_from_cash'],
        )
        messages.success(
            self.request,
            f'Added {form.cleaned_data["shares"]} {form.asset.ticker}, you now hold {holding.shares} shares',
        )
        return redirect(self.portfolio)


class HoldingUpdateView(SuccessMessageMixin, UpdateView):
    model = Holding
    form_class = HoldingForm
    template_name = 'portfolios/holding_edit.html'
    context_object_name = 'holding'

    def get_success_url(self):
        return self.object.portfolio.get_absolute_url()

    def get_success_message(self, cleaned_data):
        return f'{self.object.asset.ticker} holding was updated.'


class HoldingDeleteView(SuccessMessageMixin, DeleteView):
    model = Holding
    template_name = 'portfolios/holding_confirm_delete.html'
    context_object_name = 'holding'

    def get_success_url(self):
        return self.object.portfolio.get_absolute_url()

    def get_success_message(self, cleaned_data):
        return f'{self.object.asset.ticker} was removed from {self.object.portfolio.name}'