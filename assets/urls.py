from django.urls import path

from .views import AssetDetailView, AssetListView, RefreshPricesView


app_name = 'assets'

urlpatterns = [
    path('', AssetListView.as_view(), name='list'),
    path('refresh/', RefreshPricesView.as_view(), name='refresh'),
    path('<str:ticker>/', AssetDetailView.as_view(), name='detail'),
]