# api/serializers/product_serializer.py

from rest_framework import serializers
from ..models import PriceHistory, Product, UserLocation, Store  # Make sure Store is imported

class PriceHistorySerializer(serializers.ModelSerializer):
    store = serializers.CharField(source = 'store.name')
    location = serializers.CharField(source = 'store.location')
    price = serializers.FloatField()

    class Meta:
        model = PriceHistory
        fields = ['store', 'location', 'price']


class ProductSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['product_id', 'name', 'unit', 'price', 'image']

    def get_price(self, obj):
        prices = getattr(obj, 'latest_prices', [])
        return PriceHistorySerializer(prices, many = True).data
    
    def get_image(self, obj):
        if obj.image:
            return  f"https://res.cloudinary.com/dkkbnt3ap/image/upload/{obj.image}"
        return None   

class UserLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLocation
        fields = "__all__"


# ADD THIS - StoreSerializer
class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'store_id', 'name', 'location', 'latitude', 'longitude']


class BarcodeLookupSerializer(serializers.ModelSerializer):
    """Serializer specifically for barcode lookup with single store pricing"""
    price = serializers.SerializerMethodField()
    store_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id', 'product_id', 'name', 'unit', 'barcode', 'price', 'store_name']
    
    def get_price(self, obj):
        """Get price for the specific store passed in context"""
        store = self.context.get('store')
        if store:
            price = obj.get_price(store)
            return float(price) if price else None
        return None
    
    def get_store_name(self, obj):
        """Get the store name from context"""
        store = self.context.get('store')
        return store.name if store else None