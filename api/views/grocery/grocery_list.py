from ast import Store

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from api.models import GroceryList
from api.models.grocery import GroceryItem
from api.models.product import Product
from api.serializers.grocery_serializer import GroceryItemSerializer, GroceryListSerializer


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def grocery_lists(request):
    """
    Get all grocery lists or create a new list
    GET /api/grocery/
    POST /api/grocery/
    """
    if request.method == 'GET':
        lists = GroceryList.objects.filter(owner=request.user).prefetch_related('items__product')
        serializer = GroceryListSerializer(lists, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = GroceryListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def grocery_list_detail(request, list_id):
    """
    Delete a grocery list
    DELETE /api/grocery/{list_id}/
    """
    try:
        grocery_list = GroceryList.objects.get(id=list_id, owner=request.user)
    except GroceryList.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    grocery_list.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_item(request, list_id):
    """
    Add item to grocery list
    POST /api/grocery/{list_id}/items/
    Body: {"name": "Milk", "store_id": 1, "quantity": 1}
    """
    try:
        grocery_list = GroceryList.objects.get(id=list_id, owner=request.user)
    except GroceryList.DoesNotExist:
        return Response({'error': 'List not found'}, status=status.HTTP_404_NOT_FOUND)

    # Get data from request
    name = request.data.get('name', '').strip()
    store_id = request.data.get('store_id')

    if not name:
        return Response({'error': 'name is required'}, status=status.HTTP_400_BAD_REQUEST)
    if not store_id:
        return Response({'error': 'store_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate store exists
    try:
        store = Store.objects.get(id=store_id)
    except Store.DoesNotExist:
        return Response({'error': 'Store not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Find product by name (case-insensitive) or create new one
    try:
        product = Product.objects.get(name__iexact=name)
    except Product.DoesNotExist:
        # Create new product if not found
        product = Product.objects.create(
            name=name,
            product_id=name.lower().replace(' ', '_'),
            unit=''
        )

    # Create or get grocery item with store
    item, created = GroceryItem.objects.get_or_create(
        grocery_list=grocery_list,
        product=product,
        store=store,
        defaults={'quantity': 1}
    )

    if not created:
        # Item already exists, increment quantity
        item.quantity += 1
        item.save()

    return Response(GroceryItemSerializer(item).data, status=status.HTTP_201_CREATED)


@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def item_detail(request, list_id, item_id):
    """
    Update or delete a grocery item
    PATCH /api/grocery/{list_id}/items/{item_id}/
    Body: {"quantity": 3, "is_checked": true}
    DELETE /api/grocery/{list_id}/items/{item_id}/
    """
    try:
        item = GroceryItem.objects.get(
            id=item_id,
            grocery_list__id=list_id,
            grocery_list__owner=request.user
        )
    except GroceryItem.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PATCH':
        serializer = GroceryItemSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)