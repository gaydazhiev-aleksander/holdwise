from django.urls import path

from .views import AssetDetailView, AssetListView


app_name = 'assets'

urlpatterns = [
    path('', AssetListView.as_view(), name='list'),
    path('<str:ticker>/', AssetDetailView.as_view(), name='detail'),
]