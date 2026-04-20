from rest_framework import serializers
from api.models import PriceHistory

class PriceHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for price history model which includes all of the model atttributes for api ouutput
    """
    store = serializers.CharField(source = 'store.name')
    location = serializers.CharField(source = 'store.location')
    price = serializers.FloatField()

    class Meta:
        model = PriceHistory
        fields = ['store', 'location', 'price']
