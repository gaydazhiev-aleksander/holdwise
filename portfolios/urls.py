from django.urls import path

from .views import PortfolioDetailView, PortfolioListView, PortfolioCreateView, PortfolioUpdateView

app_name = 'portfolios'

urlpatterns = [
    path('', PortfolioListView.as_view(), name='list'),
    path('create/', PortfolioCreateView.as_view(), name='create'),
    path('<int:pk>/', PortfolioDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', PortfolioUpdateView.as_view(), name='edit'),
]
