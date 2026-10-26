from django.urls import path

from .views import (
    WatchlistListView,
    WatchlistCreateView,
    WatchlistDetailView,
    WatchlistUpdateView,
    WatchlistDeleteView,
    WatchlistAddAssetView,
    WatchlistRemoveAssetView,

)

app_name = 'watchlists'

urlpatterns = [
    path('', WatchlistListView.as_view(), name='list'),
    path('create/', WatchlistCreateView.as_view(), name='create'),
    path('<int:pk>/', WatchlistDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', WatchlistUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', WatchlistDeleteView.as_view(), name='delete'),
    path('<int:pk>/assets/add/', WatchlistAddAssetView.as_view(), name='asset-add'),
    path('<int:pk>/assets/<int:asset_pk>/remove/', WatchlistRemoveAssetView.as_view(), name='asset-remove'),
]
