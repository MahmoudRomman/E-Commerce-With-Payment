from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

# URLs that don't need language prefix
urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    
    # API routes
    path('api/', include('api_endpoints.urls')),
    path('api-auth/', include('rest_framework.urls')),  # Optional: for browsable API login/logout
]

# Language-prefixed routes (e.g. /en/, /ar/)
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', include('store.urls')),
    path('', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path('coupons/', include('coupons.urls')),

)

# Static & media files in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# | Language | URL Example                                   |
# | -------- | --------------------------------------------- |
# | English  | `http://localhost:8000/en/accounts/register/` |
# | Arabic   | `http://localhost:8000/ar/accounts/register/` |
