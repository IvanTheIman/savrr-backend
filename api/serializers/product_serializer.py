from rest_framework import serializers
from api.serializers import PriceHistorySerializer
from api.models import Product


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for product model which includes all of the model atttributes for api ouutput.Also
    includes a function to get current price from price history table, and function to get image
    for product from cloud service
    """
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



class BarcodeLookupSerializer(serializers.ModelSerializer):
    """
    Serializer for barcode lookup which includes all of the model atttributes for api ouutput.
    Also includes function to get price of item and store name.
    """
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