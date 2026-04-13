from django.urls import include, path
from django.contrib import admin

from api.views.barcode import lookup_barcode
from .views.products import products_info
from .views.user_view import location_view, profile_view, register_view
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('products_info/', products_info, name = 'products_info'),
    path('location/', location_view),
    
    path('token/', TokenObtainPairView.as_view(), name = 'token_obtaiin_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name = 'token_refresh'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name = 'token_blacklist'),

    path('register/', register_view),
    path('profile/', profile_view),

    path('products/barcode/', lookup_barcode)

    
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)