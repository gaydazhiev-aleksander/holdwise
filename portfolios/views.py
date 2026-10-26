import csv

from unittest import result

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect
from django.template.base import kwarg_re
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, FormView, ListView, UpdateView, View
from django.http import HttpResponse
from django.utils.text import slugify

from .forms import AddHoldingForm, CashMovementForm, HoldingForm, PortfolioForm, SellHoldingForm
from .models import CashMovement, Holding, Portfolio
from .services import HoldingService


def _csv_number(value, places):
    if value is None:
        return ''
    return f'{value:.{places}f}'


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


class HoldingSellView(FormView):
    form_class = SellHoldingForm
    template_name = 'portfolios/holding_sell.html'

    def dispatch(self, request, *args, **kwargs):
        self.holding = get_object_or_404(
            Holding.objects.select_related('asset', 'portfolio'),
            pk=kwargs['pk'],
        )
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial['price'] = self.holding.asset.last_price
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['holding'] = self.holding
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['holding'] = self.holding
        return context

    def form_valid(self, form):
        shares = form.cleaned_data['shares']
        price = form.cleaned_data['price']
        result = HoldingService().sell(self.holding, shares, price)
        portfolio = self.holding.portfolio

        messages.success(
            self.request,
            f'Sold {shares.normalize():f} {self.holding.asset.ticker} at {price:,.2f} '
            f'for {result.proceeds:,.2f} (profit/loss: {result.profit_loss:+,.2f}) '
            f'Cash balance: {portfolio.cash_balance:,.2f}.',
        )
        return redirect(portfolio)


class CashMovementCreateView(CreateView):
    model = CashMovement
    form_class = CashMovementForm
    template_name = 'portfolios/cash_form.html'

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
        form.instance.portfolio = self.portfolio
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'{self.object.get_movement_type_display()} of {self.object.amount:,.2f} recorded '
            f'Cash balance: {self.portfolio.cash_balance:,.2f}',
        )
        return response

    def get_success_url(self):
        return self.portfolio.get_absolute_url()


class CashMovementListView(ListView):
    template_name = 'portfolios/cash_history.html'
    context_object_name = 'movements'
    paginate_by = 15

    def get_queryset(self):
        self.portfolio = get_object_or_404(Portfolio, pk=self.kwargs['pk'])
        return self.portfolio.cash_movements.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['portfolio'] = self.portfolio
        return context


class PortfolioExportView(View):
    def get(self, request, pk):
        portfolio = get_object_or_404(Portfolio.objects.prefetch_related('holdings__asset'), pk=pk)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{slugify(portfolio.name)}-holdings.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Ticker', 'Name', 'Type', 'Shares', 'Average buy price', 'Last price',
            'Cost basis', 'Market value', 'Profit/loss', 'Profit/loss %',
        ])

        for holding in portfolio.holdings.all():
            writer.writerow([
                holding.asset.ticker,
                holding.asset.name,
                holding.asset.get_asset_type_display(),
                _csv_number(holding.shares, 6),
                _csv_number(holding.average_buy_price, 2),
                _csv_number(holding.asset.last_price, 2),
                _csv_number(holding.cost_basis, 2),
                _csv_number(holding.current_value, 2),
                _csv_number(holding.profit_loss, 2),
                _csv_number(holding.profit_loss_percent, 2),
            ])

        writer.writerow([])
        writer.writerow(['Cash', '', '', '', '', '', '', _csv_number(portfolio.cash_balance, 2)])

        return response