from django.urls import include, path
from django.contrib import admin

from api.services.barcode import lookup_barcode
from api.views.barcode.barcode_lookup_view import barcode_lookup_view
from api.views.grocery_list import  grocery_lists, store_list
from .views.products import products_info
from .views.user_view import location_view, register_view, geocode_zipcode
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('products_info/', products_info, name = 'products_info'),
    path('location/', location_view),
    
    path('token/', TokenObtainPairView.as_view(), name = 'token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name = 'token_refresh'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name = 'token_blacklist'),

    path('register/', register_view),

    path('products/barcode/', lookup_barcode),

    path('grocery/', grocery_lists),

    path('stores/', store_list),

    path('products/barcode/<str:barcode>/', barcode_lookup_view, name='barcode-lookup'),

    path('location/geocode/', geocode_zipcode, name='geocode-zipcode'),

   
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)