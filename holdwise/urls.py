from django.contrib import admin
from django.urls import include, path

from assets.views import AssetListView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('assets/', include('assets.urls')),
    path('', include('common.urls')),
]
