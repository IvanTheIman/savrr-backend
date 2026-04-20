from django.contrib import admin
from api.models import Product

from django.contrib import admin
from .models import Store, Product, ProductBarcode, PriceHistory

class ProductBarcodeInline(admin.TabularInline):
    model = ProductBarcode
    extra = 1
    fields = ['barcode', 'variant_name', 'source']

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'product_id', 'unit', 'get_barcode_count']
    inlines = [ProductBarcodeInline]
    
    def get_barcode_count(self, obj):
        return obj.barcodes.count()
    get_barcode_count.short_description = 'Barcodes'

class ProductBarcodeAdmin(admin.ModelAdmin):
    list_display = ['barcode', 'product', 'variant_name', 'source', 'added_at']
    list_filter = ['source', 'added_at']
    search_fields = ['barcode', 'product__name']

admin.site.register(Product, ProductAdmin)
admin.site.register(ProductBarcode, ProductBarcodeAdmin)
admin.site.register(Store)
admin.site.register(PriceHistory)

