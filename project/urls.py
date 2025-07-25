from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', include('core.urls', namespace='core')),
    path('accounts/', include('accounts.urls')),
    path('', include('store.urls')),
    path('', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path('coupons/', include('coupons.urls')),





] 
urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)
