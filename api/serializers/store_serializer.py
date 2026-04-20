from rest_framework import serializers
from api.models import Store


class StoreSerializer(serializers.ModelSerializer):
    """
    Serializer for store model which includes all of the model atttributes for api ouutput
    """
    class Meta:
        model = Store
        fields = ('id', 'name', 'location')