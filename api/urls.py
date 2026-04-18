from django.urls import include, path
from django.contrib import admin

from api.services.barcode import lookup_barcode
from api.views.barcode_product_view import add_barcode_to_product, barcode_lookup_view
from api.views.grocery_list import add_item, grocery_list_detail, grocery_lists, item_detail, store_list
from .views.products import products_info
from .views.user_view import location_view, profile_view, register_view
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
    path('profile/', profile_view),

    path('products/barcode/', lookup_barcode),

    path('grocery/', grocery_lists),
    path('grocery/<int:list_id>/', grocery_list_detail),
    path('grocery/<int:list_id>/items/', add_item),
    path('grocery/<int:list_id>/items/<int:item_id>/', item_detail),

    path('stores/', store_list),

    path('products/barcode/<str:barcode>/', barcode_lookup_view, name='barcode-lookup'),

    path('products/search/', search_products, name='search_products'),
    path('products/<str:product_id>/add-barcode/', add_barcode_to_product, name='add_barcode'),
    path('products/barcode/<str:barcode>/', get_product_by_barcode, name='get_product_by_barcode'),

    
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)