from django.urls import path

from .views import (
    CashMovementCreateView,
    CashMovementListView,
    HoldingCreateView,
    HoldingDeleteView,
    HoldingSellView,
    HoldingUpdateView,
    PortfolioCreateView,
    PortfolioDeleteView,
    PortfolioDetailView,
    PortfolioListView,
    PortfolioUpdateView,
)

app_name = 'portfolios'

urlpatterns = [
    path('', PortfolioListView.as_view(), name='list'),
    path('create/', PortfolioCreateView.as_view(), name='create'),
    path('<int:pk>/', PortfolioDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', PortfolioUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', PortfolioDeleteView.as_view(), name='delete'),
    path('<int:pk>/holdings/add/', HoldingCreateView.as_view(), name='holding-add'),
    path('<int:pk>/cash/', CashMovementListView.as_view(), name='cash-history'),
    path('<int:pk>/cash/add/', CashMovementCreateView.as_view(), name='cash-add'),
    path('holdings/<int:pk>/edit/', HoldingUpdateView.as_view(), name='holding-edit'),
    path('holdings/<int:pk>/delete/', HoldingDeleteView.as_view(), name='holding-delete'),
    path('holdings/<int:pk>/sell/', HoldingSellView.as_view(), name='holding-sell'),
]