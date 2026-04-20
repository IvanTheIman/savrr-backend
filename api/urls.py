from django.urls import path
from django.contrib import admin
from api.services.barcode.barcode_lookup import lookup_barcode
from api.views import (
    barcode_lookup_view,
    grocery_lists,
    location_view,
    register_view,
    geocode_zipcode,
)
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView

from api.views.grocery.products import products_info

urlpatterns = [
    path('admin/', admin.site.urls),

    path('products_info/', products_info, name = 'products_info'),
    path('location/', location_view),
    path('location/geocode/', geocode_zipcode, name='geocode-zipcode'),
    
    path('token/', TokenObtainPairView.as_view(), name = 'token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name = 'token_refresh'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name = 'token_blacklist'),

    path('register/', register_view),

    path('products/barcode/', lookup_barcode),
    path('products/barcode/<str:barcode>/', barcode_lookup_view, name='barcode-lookup'),

    path('grocery/', grocery_lists),


   
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)