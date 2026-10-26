from django.urls import path

from .views import PortfolioDetailView, PortfolioListView, PortfolioCreateView, PortfolioUpdateView, PortfolioDeleteView, HoldingCreateView, HoldingUpdateView, HoldingDeleteView, HoldingSellView

app_name = 'portfolios'

urlpatterns = [
    path('', PortfolioListView.as_view(), name='list'),
    path('create/', PortfolioCreateView.as_view(), name='create'),
    path('<int:pk>/', PortfolioDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', PortfolioUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', PortfolioDeleteView.as_view(), name='delete'),
    path('<int:pk>/holdings/add/', HoldingCreateView.as_view(), name='holding-add'),
    path('holdings/<int:pk>/edit/', HoldingUpdateView.as_view(), name='holding-edit'),
    path('holdings/<int:pk>/delete/', HoldingDeleteView.as_view(), name='holding-delete'),
    path('holdings/<int:pk>/sell/', HoldingSellView.as_view(), name='holding-sell'),
]
