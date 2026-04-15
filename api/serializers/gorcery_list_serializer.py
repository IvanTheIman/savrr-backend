from rest_framework import serializers
from api.models import GroceryList, GroceryItem, Product, Store

class GroceryItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = GroceryItem
        fields = ('id', 'product', 'product_name', 'quantity', 'is_checked')

class GroceryListSerializer(serializers.ModelSerializer):
    items = GroceryItemSerializer(many=True, read_only=True)

    class Meta:
        model = GroceryList
        fields = ('id', 'name', 'store', 'created_at', 'items')
        read_only_fields = ('owner',)
