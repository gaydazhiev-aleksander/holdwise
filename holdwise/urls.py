from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('assets/', include('assets.urls')),
    path('portfolios/', include('portfolios.urls')),
    path('watchlists/', include('watchlists.urls')),
    path('', include('common.urls')),
]