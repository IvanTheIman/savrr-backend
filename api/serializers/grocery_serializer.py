from rest_framework import serializers
from api.models import GroceryList, GroceryItem

class GroceryItemSerializer(serializers.ModelSerializer):
    """
    Serializer for grocery item model which includes all of the model atttributes for api ouutput
    """
    product_name = serializers.CharField(source='product.name', read_only=True)
    store_name = serializers.CharField(source = 'store.name', read_only = True)

    class Meta:
        model = GroceryItem
        fields = ('id', 'product', 'product_name','store', 'store_name', 'quantity', 'is_checked')

    def get_store_name(self, obj):
        # Handle null stores gracefully
        return obj.store.name if obj.store else "No store"

class GroceryListSerializer(serializers.ModelSerializer):
    """
    Serializer for grocery list model which includes all of the model atttributes for api ouutput
    """
    items = GroceryItemSerializer(many=True, read_only=True)

    class Meta:
        model = GroceryList
        fields = ('id', 'name', 'created_at', 'items')
        read_only_fields = ('owner',)