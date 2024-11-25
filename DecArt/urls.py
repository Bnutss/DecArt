from DecArt import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls', namespace='users')),
    path('directory/', include('directory.urls', namespace='directory')),
    path('warehouses/', include('warehouses.urls', namespace='warehouses')),
    path('sales/', include('sales.urls', namespace='sales')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
