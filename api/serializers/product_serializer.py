from rest_framework import serializers
from ..models import PriceHistory, Product, UserLocation

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